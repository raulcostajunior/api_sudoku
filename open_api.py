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
from api.board import get_board_state_flags
from api.board_schemas import BoardSchema, BoardFlagsSchema

with app.test_request_context():
    spec.path(view=get_board_state_flags)

import json
with open("swagger.json", "w") as f:
    json.dump(spec.to_dict(), f)


