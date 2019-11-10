from api import rest_api, InvalidUsage
from flask import current_app, request, Response, jsonify

import py_libsudoku as lsdk

# List of board generation jobs.
# Each entry is a dictionary with the following keys:
#   "job_id": unique id of a generation job.
#   "job_start_time": time the gen job started.
#   "job_finish_time": time the gen job finished.
#   "current_gen_step": current step of the generation job.
#   "total_steps": total number of steps for the generation job.
#   "gen_board": resulting generated board (None if the job isn't completed).
gen_jobs = []

# The id to use for the next board generation job.
gen_job_id = 0

# Maximum number of running generation jobs that can be running at a given
# time.
MAX_RUN_GEN_JOBS = 16

# Maximum time, in minutes, a generation job can be kept in the gen_jobs
# list.
MAX_GEN_JOB_AGE = 20


@rest_api.route("board/", methods=["POST"])
def post_board():
    global gen_job_id
    try:
        dif_level = int(request.args.get("difficulty-level"))
    except:
        raise (InvalidUsage("Bad request: 'difficulty-level' parameter required."))
    if dif_level < 1 or dif_level > 3:
        raise InvalidUsage(
            "Bad request: invalid difficulty level, '{}'".format(dif_level), 400
        )
    board_level = lsdk.PuzzleDifficulty.HARD
    if dif_level == 1:
        board_level = lsdk.PuzzleDifficulty.EASY
    elif dif_level == 2:
        board_level = lsdk.PuzzleDifficulty.MEDIUM
    # Clear all the "expired" jobs - those that have been started more than
    # MAX_RUN_GEN_JOBS minutes ago, independently of their current status.
    # Also gathers the number of non-expired running jobs.
    running_jobs = 0
    # TODO sweep the gen_jobs under a lock protection.

    # TODO return a 503 if the maximum number of running jobs has been reached

    gen_job_id += 1
    # Captures the current job id to use in the progress callback.
    current_job_id = gen_job_id
    # TODO launch the generation job on a background non daemon thread.

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

