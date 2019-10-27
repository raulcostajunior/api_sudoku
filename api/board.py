from api import rest_api
from flask import request, jsonify, make_response

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
              content:
                application/json:
                  schema: BoardFlagsSchema
            400:
              description: invalid board parameter
    """
    body = request.get_json()
    b = lsdk.Board(body["board"])
    d = {
        "isValid": b.isValid,
        "isEmpty": b.isEmpty,
        "isComplete": b.isComplete,
        }
    return jsonify(d)
