from api import (
  get_executor,
  rest_api, InvalidUsage
)
from flask import (
    current_app, jsonify, make_response,
    request, Response, url_for
)

import threading
import time
import uuid

import py_libsudoku as lsdk

# job_info is a dictionary that has the job_id for key and another dictionary
# as the value. The second level dictionary has the following keys:
#  - cancel: either True or False to indicate the worker if it should stop or
#            proceed to the end.
#  - progress_percent: current progress percentage for the job (0.0 to 100.0)
#  - num_solutions: number of solutions found so far.
job_info = {}

job_info_lock = threading.Lock()


@rest_api.route('solved-board/all', methods=['POST'])
def create_all_solved_boards_async():
    """Starts a search for all the solutions for a given board.
    ---
    post:
        tags:
          - Solved Boards
        summary: Starts a search for all the solutions for a given board 
                 (may take a while).
        requestBody:
            description: The board to be solved
            required: true
            content:
              application/json:
                schema: BoardSchema
        responses:
            202:
              description: The search has been started. The url for querying the
                           search progress is returned in the "location" header
                           of the response.
            400:
              description: Error detail in "message".
    """
    global job_info
    global job_info_lock
    board = lsdk.Board()
    try:
        body = request.get_json()
        board = lsdk.Board(body["board"]) # Board to solve
    except Exception as e:
        raise(InvalidUsage("Bad request: {}".format(str(e)), 400))

    executor = get_executor()

    # Invokes the solving worker giving a unique id to index the
    # corresponding future. This unique id will then be passed to the
    # solving status endpoint so it knows which future to query.
    location_value = ""
    current_job_id = str(uuid.uuid4())
    with job_info_lock:
        info = {"progress_percent":0.0, "num_solutions":0, "cancel":False}
        job_info[current_job_id] = info
    executor.submit_stored(current_job_id,
                           solve_board_worker, board, current_job_id)

    location_value = url_for('api.get_solve_status', job_id=current_job_id)
    response = current_app.response_class(status=202)
    response.headers["Location"] = location_value
    return response


@rest_api.route("solved-board/all/status/<job_id>")
def get_solve_status(job_id):
    """Returns the status of a search for all the solutions of a given
       board.
    ---
    get:
        tags:
          - Solved Boards
        summary: Returns the status of a search for all the solutions of a given
                 board.
        parameters:
          - name: job_id
            in: path
            required: true
            description: the id of the search solutions job
            schema:
              type: string
        responses:
            200:
              description: If the search is not finished returns a
                           json with the fields "progress_percent" and
                           "num_solutions" for the progress percentage
                           and the number of solutions found so far. 
                           If the search is finished, returns a json with
                           the structure below.
              content:
                application/json:
                  schema: BoardSolutionsSchema
            404:
              description: The job_id doesn't refer to a known job.
    """
    global job_info
    global job_info_lock
    executor = get_executor()
    fut = None
    try:
        fut = executor.futures._futures[job_id]
    except KeyError:
        return make_response(
            jsonify(
                {"status": "no board solving for job-id '{}'".format(
                    job_id)},
            ), 404
         )
    if not fut.done():
        resp = {"status":"solving"}
        with job_info_lock:
            resp["progress_percent"] = job_info[job_id]["progress_percent"]
            resp["num_solutions"] = job_info[job_id]["num_solutions"]
        return jsonify(resp)
    else:
        fut = executor.futures.pop(job_id)
        with job_info_lock:
            job_info.pop(job_id)
        return jsonify(fut.result())


@rest_api.route("solved-board/all/<job_id>", methods=['DELETE'])
def cancel_async_solve(job_id):
    """Cancels an ongoing search for all the solutions of a board.
    ---
    delete:
        tags:
          - Solved Boards
        summary: Cancels an ongoing search for all the solutions of a board.
        parameters:
          - name: job_id
            in: path
            description: The id of the search job to be cancelled.
            required: true
            schema:
              type: string
        responses:
            204:
              description: The search has been cancelled.
            404:
              description: The given job_id does not correspond to a known
                           ongoing search job.
    """
    global job_info
    global job_info_lock
    executor = get_executor()
    fut = None
    try:
        fut = executor.futures._futures[job_id]
    except KeyError:
        return make_response(
            jsonify(
                {"status": "no board solving to cancel for job-id '{}'".format(
                    job_id)}), 404
        )
    if not fut.done():
        # Marks the job to be stopped as soon as possible by the worker.
        with job_info_lock:
            job_info[job_id]["cancel"] = True
    else: 
        # The job has been done but a cancel has been invoked, there's a
        # chance that no request for its result will come - do the clean-
        # up from here.
        executor.futures.pop(job_id)
    response = current_app.response_class(status=204)
    return response


@rest_api.route('solved-board/one', methods=['POST'])
def create_one_solved_board():
    """Returns one solution for a given board.
    ---
    post:
        tags:
          - Solved Boards
        summary: Returns one solution for a given board.
        requestBody:
            description: The board to be solved
            required: true
            content:
              application/json:
                schema: BoardSchema
        responses:
            200:
              description: A solution for the given board
              content:
                application/json:
                  schema: SolvedBoardSchema
            400:
              description: Error detail in "message".
    """
    s = lsdk.Board() # Board to hold the solution
    result = lsdk.SolverResult.NO_ERROR

    try:
        body = request.get_json()
        b = lsdk.Board(body["board"]) # Board to solve
        solver = lsdk.Solver()
        result = solver.solve(b, s)
    except Exception as e:
        raise(InvalidUsage("Bad request: {}".format(str(e)), 400))

    if result == lsdk.SolverResult.NO_ERROR:
        return jsonify({"board" : [v for v in s]})
    else:
        raise(InvalidUsage("Not solvable: {}".format(result), 400))


def solve_board_worker(board, job_id):
    global job_info
    global job_info_lock

    start_time = time.time()

    board_solutions = []
    solver_result = lsdk.SolverResult.NO_ERROR

    solver = lsdk.Solver()

    asyncSolveCompleted = False

    # Handler for solving progress
    def on_solver_progress(progress_percent, num_solutions):
        global job_info
        global job_info_lock
        nonlocal job_id
        with job_info_lock:
            job_info[job_id]["progress_percent"] = progress_percent
            job_info[job_id]["num_solutions"] = num_solutions

    # Handler for solving finished: captures the results.
    def on_solver_finished(result, solutions):
        global job_info
        global job_info_lock
        nonlocal job_id
        nonlocal asyncSolveCompleted
        asyncSolveCompleted = True
        nonlocal solver_result
        solver_result = result
        nonlocal board_solutions
        board_solutions = solutions
        if result == lsdk.SolverResult.ASYNC_SOLVED_CANCELLED:
            # Job has been cancelled externally - cleans-up.
            executor = get_executor()
            with job_info_lock:
                job_info.pop(job_id)
                executor.futures.pop(job_id)

    solver.asyncSolveForGood(
         board,
         on_solver_progress,
         on_solver_finished
    )

    while not asyncSolveCompleted:
        with job_info_lock:
            if job_info[job_id]["cancel"]:
                # Job has been cancelled externally - stops and cleans-up.
                solver.cancelAsyncSolving()
        time.sleep(0.1)

    finish_time = time.time()

    # Set future result
    solved_boards = []
    for n in range(0, len(board_solutions)):
        # Board is not JSON serializable.
        # That's the reason for the list compreheension.
        solved_boards.append([val for val in board_solutions[n]])
    status = (
        "Cancelled" if solver_result == lsdk.SolverResult.ASYNC_SOLVED_CANCELLED
        else "Ok"
    )
    fut_result = {
        # SolverResult is not JSON serializable.
        # That's the reason for the str explicit conversion.
        "status": status,
        "solved_boards": solved_boards,
        "solve_time": finish_time - start_time
    }

    return fut_result

