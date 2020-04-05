import json
from api.schemas import (
    BoardSchema, BoardPositionSchema,
    BoardStatusSchema, SolvedBoardSchema,
    BoardSolutionsSchema, GeneratedBoardSchema,
    SolveAllSchema
)
from api.solved_board import (
    create_all_solved_boards_async,
    create_one_solved_board,
    get_solve_status, cancel_async_solve
)
from api.board import (
    gen_board_async, get_gen_status,
    get_board_status
)
from api_runner import app
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

spec = APISpec(
    title="py_libsudoku api",
    version="1.0.6",
    openapi_version="3.0.2",
    info=dict(
        description="Api for generating and solving Sudoku puzzles. "
        "Based on [py-libsudoku](https://pypi.org/project/py-libsudoku)."
    ),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


with app.test_request_context():
    spec.path(view=get_board_status)
    spec.path(view=create_one_solved_board)
    spec.path(view=create_all_solved_boards_async)
    spec.path(view=get_solve_status)
    spec.path(view=cancel_async_solve)
    spec.path(view=gen_board_async)
    spec.path(view=get_gen_status)

with open("static/swagger.json", "w") as f:
    json.dump(spec.to_dict(), f)
