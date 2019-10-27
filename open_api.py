from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

spec = APISpec(
    title="py_libsudoku",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="Python extension for generating and solving Sudoku puzzles - based on libsudoku."
    ),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

from marshmallow import Schema, fields

class BoardFlagsSchema(Schema):
    isValid = fields.Bool()
    isComplete = fields.Bool()
    isEmpty = fields.Bool()

spec.components.schema("BoardFlagsSchema", schema=BoardFlagsSchema)

from api_runner import app
from api.board import get_board_state_flags

with app.test_request_context():
    spec.path(view=get_board_state_flags)

import json
with open("swagger.json", "w") as f:
    json.dump(spec.to_dict(), f)


