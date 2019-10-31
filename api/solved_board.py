from api import rest_api, InvalidUsage
from flask import request, Response, jsonify

import py_libsudoku as lsdk

@rest_api.route('solved-board/', methods=['POST'])
def create_solved_board():
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
        s_values = [v for v in s]
        d = {
          "board": s_values
        }
        return jsonify(d)
    else:
        raise(InvalidUsage("Not solvable: {}".format(result), 400))
