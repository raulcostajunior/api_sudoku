from api import rest_api, InvalidUsage
from flask import (
    current_app, jsonify, make_response,
    request, Response, url_for
)
from flask_executor import Executor

import threading
import time
import uuid

import py_libsudoku as lsdk

# The flask-executor that will be lazily instantiated
executor = None
# Lock to guarantee single lazy instantiation of executor
executor_lock = threading.Lock()

def create_executor_if_needed():
    # Lazy instatiantion of the executor
    global executor
    global executor_lock
    executor_lock.acquire()
    if not executor:
        executor = Executor(current_app)
    executor_lock.release()
    
@rest_api.route("board/gen-status/<job_id>")
def get_gen_status(job_id):
    create_executor_if_needed()
    future = executor.futures.pop(job_id)
    if not future:
        return make_response(
            jsonify(
                {"status": "no board generation for job-id '{}'".format(
                    job_id)},
                404
            )
         )
    elif not future.done():
        return jsonify({"status": "generating"})
    else:
        return jsonify(future.result())


@rest_api.route("board/", methods=["POST"])
def post_board():
    try:
        dif_level = int(request.args.get("difficulty-level"))
    except:
        raise (
            InvalidUsage(
                "Bad request: 'difficulty-level' parameter required with value in [1, 2, 3]."
            )
        )
    if dif_level < 1 or dif_level > 3:
        raise InvalidUsage(
            "Bad request: invalid difficulty level, '{}'".format(
                dif_level), 400
        )
    board_level = lsdk.PuzzleDifficulty.HARD
    if dif_level == 1:
        board_level = lsdk.PuzzleDifficulty.EASY
    elif dif_level == 2:
        board_level = lsdk.PuzzleDifficulty.MEDIUM

    create_executor_if_needed()

    # Invokes the generation worker giving a unique id to index the
    # corresponding future. This unique id will then be passed to the
    # generation status endpoint so it knows which future to query.
    location_value = ""
    current_job_id = str(uuid.uuid4())
    executor.submit_stored(current_job_id,
                           gen_board_worker, board_level)

    location_value = url_for('api.get_gen_status', job_id=current_job_id)
    response = current_app.response_class(status=202)
    response.headers["Location"] = location_value
    return response


@rest_api.route("board/state-flags")
def get_board_state_flags():
    """Retrieves the state flags of a given board (the board goes in JSON format in the body).
    ---
    get:
        tags:
          - Boards
        summary: Retrieves the state flags of a given board
        requestBody:
            description: The board to be evaluated
            required: true
            content:
              application/json:
                schema: BoardSchema
        responses:
            200:
              description: Values of the state flags
              content:
                application/json:
                  schema: BoardFlagsSchema
            400:
              description: Error detail in "message".
    """
    try:
        body = request.get_json()
        b = lsdk.Board(body["board"])
        d = {
            "isValid": b.isValid,
            "isEmpty": b.isEmpty,
            "isComplete": b.isComplete,
        }
        return jsonify(d)
    except Exception as e:
        raise (InvalidUsage("Bad request: {}".format(str(e)), 400))


def gen_board_worker(difficulty_level):
    """Generates a board with the given difficulty_level. 
    Returns a dictionary with the following keys: 
    . "gen_result": one of the values of GeneratorResult
    . "gen_board": the generated board if any
    . "start_time"
    . "finish_time"
    """
    start_time = time.time()

    gen_board = lsdk.Board()
    gen_result = lsdk.GeneratorResult.NO_ERROR

    gen = lsdk.Generator()

    asyncGenCompleted = False

    # Handler for generation finished: captures the results.
    def on_gen_finished(result, board):
        nonlocal asyncGenCompleted
        asyncGenCompleted = True
        nonlocal gen_result
        gen_result = result
        nonlocal gen_board
        gen_board = board

    gen.asyncGenerate(difficulty_level,
                      None,  # Does nothing on progress
                      on_gen_finished
                      )
    while not asyncGenCompleted:
        time.sleep(0.1)

    finish_time = time.time()

    # Set future result
    fut_result = {
        # GenerationResult is not JSON serializable.
        # That's the reason for the str explicit conversion.
        "gen_result": str(gen_result),
        # Board is not JSON serializable.
        # That's the reason for the list compreheension
        "gen_board": [val for val in gen_board],
        "start_time": start_time,
        "finish_time": finish_time
    }

    return fut_result
