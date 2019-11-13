from api import rest_api, InvalidUsage
from flask import current_app, request, Response, jsonify
from flask_executor import Executor

import py_libsudoku as lsdk

# The id to use for the next board generation job.
gen_job_id = 0

# Executor to be lazily instantiated.
executor = None


def gen_board_worker(difficulty_level, gen_job_id):
    """Generates a board with the given difficulty_level. 
  Returns a dictionary with the following keys: 
    . "gen_result": one of the values of GeneratorResult
    . "gen_board": the generated board if any
    . "start_time"
    . "finish_time"
  """
    # TODO use job_id to keep track of progress information - the callback updates a structure indexed by job_id. That is the info returned by the progress tracking end-point.
    pass


@rest_api.route("board/", methods=["POST"])
def post_board():
    global gen_job_id
    global executor
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
            "Bad request: invalid difficulty level, '{}'".format(dif_level), 400
        )
    board_level = lsdk.PuzzleDifficulty.HARD
    if dif_level == 1:
        board_level = lsdk.PuzzleDifficulty.EASY
    elif dif_level == 2:
        board_level = lsdk.PuzzleDifficulty.MEDIUM

    # TODO - put the next three instructions under a lock protection
    if not executor:
        executor = Executor(current_app)
    gen_job_id += 1
    current_job_id = gen_job_id
    executor.submit_stored(str(current_job_id), gen_board_worker, board_level, current_job_id)

    response = current_app.response_class(status=202)
    # TODO use the appropriate url reverting mechanism to generate the location
    response.headers["Location"] = "v1/sudoku-board/status/{}".format(current_job_id)
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

