from api import rest_api, InvalidUsage
from flask import request, Response, jsonify

import py_libsudoku as lsdk 

@rest_api.route('board/state-flags')
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
        raise(InvalidUsage("Bad request: {}".format(str(e)), 400))

