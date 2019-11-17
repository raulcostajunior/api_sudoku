from api import (
  create_executor_if_needed,
  rest_api, InvalidUsage
)
from flask import (
    current_app, jsonify, make_response,
    request, Response, url_for
)

import time
import uuid

import py_libsudoku as lsdk

@rest_api.route("solved-board/all/status/<job_id>")
def get_solve_status(job_id):
    executor = create_executor_if_needed()
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
        # TODO add progress info to the response body
        return jsonify({"status": "solving"})
    else:
        fut = executor.futures.pop(job_id)
        return jsonify(fut.result())

# TODO Define cancel_async_solve endpoint

@rest_api.route('solved-board/all', methods=['POST'])
def create_all_solved_boards_async():
    board = lsdk.Board()
    try:
        body = request.get_json()
        board = lsdk.Board(body["board"]) # Board to solve
    except Exception as e:
        raise(InvalidUsage("Bad request: {}".format(str(e)), 400))

    executor = create_executor_if_needed()

    # Invokes the solving worker giving a unique id to index the
    # corresponding future. This unique id will then be passed to the
    # solving status endpoint so it knows which future to query.
    location_value = ""
    current_job_id = str(uuid.uuid4())
    executor.submit_stored(current_job_id,
                           solve_board_worker, board)

    location_value = url_for('api.get_solve_status', job_id=current_job_id)
    response = current_app.response_class(status=202)
    response.headers["Location"] = location_value
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
                  schema: BoardSchema
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

def solve_board_worker(board):
    start_time = time.time()

    board_solutions = []
    solver_result = lsdk.SolverResult.NO_ERROR

    solver = lsdk.Solver()

    asyncSolveCompleted = False

    # Handler for solving finished: captures the results.
    def on_solver_finished(result, solutions):
        nonlocal asyncSolveCompleted
        asyncSolveCompleted = True
        nonlocal solver_result
        solver_result = result
        nonlocal board_solutions
        board_solutions = solutions

    solver.asyncSolveForGood(
         board,
         # TODO store progress info on auxiliary structure
         None,  # Does nothing on progress (for now)
         on_solver_finished
    )

    while not asyncSolveCompleted:
        time.sleep(0.1)

    finish_time = time.time()

    # Set future result
    solved_boards = {}
    solved_boards["board_count"] = len(board_solutions)
    for n in range(1, len(board_solutions)+1):
        solved_boards[f"board#{n}"] =  [val for val in board_solutions[n-1]]
    fut_result = {
        # SolverResult is not JSON serializable.
        # That's the reason for the str explicit conversion.
        "status": str(solver_result),
        # Board is not JSON serializable.
        # That's the reason for the list compreheension
        "solved_boards": solved_boards,
        "solve_time": finish_time - start_time
    }

    return fut_result

