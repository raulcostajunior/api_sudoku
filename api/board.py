from api import (
    get_executor,
    rest_api, InvalidUsage
)
from flask import (
    current_app, jsonify, make_response,
    request, Response, url_for
)
from flask_executor import Executor

import time
import uuid

import py_libsudoku as lsdk

@rest_api.route("board/gen-status/<job_id>")
def get_gen_status(job_id):
    """Retrieves the status of a generate board request given its job id.
    ---
    get:
        tags:
          - Boards
        summary: Retrieves the status of a generate board request given its job id.
        parameters:
          - name: job_id
            in: path
            required: true
            description: the id of the generate board job.
            schema:
              type: string
        responses:
            200:
              description: If the generation is not finished returns a
                           json with the fields "current_step" and
                           "total_steps". If the board has been generated,
                           returns the content described below.
              content:
                application/json:
                  schema: GeneratedBoardSchema
            404:
              description: The job_id doesn't refer to a known job.
    """
    executor = get_executor()
    fut = None
    try:
        fut = executor.futures._futures[job_id]
    except KeyError:
        return make_response (
            jsonify(
                {"message": "no board generation for job-id '{}'".format(
                    job_id)},
            ), 404
        )
    if not fut.done():
        return jsonify({"status": "generating"})
    else:
        fut = executor.futures.pop(job_id)
        return jsonify(fut.result())


@rest_api.route("board/", methods=["POST"])
def gen_board_async():
    """Starts the generation of a Board with a given difficulty level.
    ---
    post:
        tags:
          - Boards
        summary: Starts the generation of a Board with a given difficulty level.
        parameters:
          - name: difficulty-level
            in: query
            description: The difficulty level. Possible values are 1 (easy), 2
                         (medium) or 3 (difficult).
            required: true
            schema:
              type: integer
              enum: [1, 2, 3]
        responses:
            202:
              description: The generation has been started. The url for querying the
                           search progress is returned in the "location" header
                           of the response.
            400:
              description: Error detail in "message".
    """
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

    executor = get_executor()

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


@rest_api.route("board/status", methods=["POST"])
def get_board_status():
    """Retrieves the status of a given board (the board goes in JSON format in the body).
    ---
    post:
        tags:
          - Boards
        summary: Retrieves the status of a given board.
        requestBody:
            description: The board to be evaluated
            required: true
            content:
              application/json:
                schema: BoardSchema
        responses:
            200:
              description: The status of the board.
              content:
                application/json:
                  schema: BoardStatusSchema
            400:
              description: Error detail in "message".
    """
    try:
        body = request.get_json()
        b = lsdk.Board(body["board"])
        invalid_positions = b.getInvalidPositions()
        d = {
            "isValid": b.isValid,
            "isEmpty": b.isEmpty,
            "isComplete": b.isComplete,
            "invalidPositions": [(p[0], p[1]) for p in invalid_positions]
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
        "status": str(gen_result),
        # Board is not JSON serializable.
        # That's the reason for the list compreheension
        "board": [val for val in gen_board],
        "gen_time": finish_time - start_time
    }

    return fut_result
