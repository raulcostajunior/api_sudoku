from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

spec = APISpec(
    title="py_libsudoku",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description=
           "Python extension for generating and solving Sudoku puzzles. "
           "Based on C++ [libsudoku](https://github.com/raulcostajunior/libsudoku)."
    ),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

from api_runner import app
from api.board import (
    gen_board_async, get_gen_status,
    get_board_state_flags
)
from api.solved_board import (
    create_all_solved_boards_async,
    create_one_solved_board, 
    get_solve_status, cancel_async_solve
)
from api.schemas import (
    BoardSchema, BoardFlagsSchema,
    SolvedBoardSchema, BoardSolutionsSchema,
    GeneratedBoardSchema
)

with app.test_request_context():
    spec.path(view=get_board_state_flags)
    spec.path(view=create_one_solved_board)
    spec.path(view=create_all_solved_boards_async)
    spec.path(view=get_solve_status)
    spec.path(view=cancel_async_solve)
    spec.path(view=gen_board_async)
    spec.path(view=get_gen_status)

import json
with open("swagger.json", "w") as f:
    json.dump(spec.to_dict(), f)


