from marshmallow import Schema, fields, validate

class BoardSchema(Schema):
    board = fields.List(
        fields.Integer(validate=validate.Range(min=0,  max=9)),
        required=True,
        validate=validate.Length(1, 81)
    )

class BoardFlagsSchema(Schema):
    isValid = fields.Bool(description="Any invalid or repeated value?", required=True)
    isComplete = fields.Bool(description="All positions filled and valid?"
                             , required=True)
    isEmpty = fields.Bool(
        description="No position filled?", 
        required=True
    )

class SolvedBoardSchema(Schema):
    board = fields.List(
        fields.Integer(validate=validate.Range(min=0,  max=9)),
        required=True,
        validate=validate.Length(81)
    )

class BoardSolutionsSchema(Schema):
    solve_time = fields.Float(
        description="Elapsed time, in seconds, for finding all solutions.",
        required=True
    )
    solved_boards = fields.List(
        fields.Nested(SolvedBoardSchema), 
        required=True
    )
    status = fields.String(
        description='Either "Cancelled" or "Ok".',
        required=True
    )
