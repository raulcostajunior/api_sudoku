from marshmallow import Schema, fields, validate

class BoardSchema(Schema):
    board = fields.List(
        fields.Integer(validate=validate.Range(min=0,  max=9)),
        required=True,
        validate=validate.Length(1, 81)
    )

class BoardFlagsSchema(Schema):
    isValid = fields.Bool(description="Any invalid or repeated value?")
    isComplete = fields.Bool(description="All positions filled and valid?")
    isEmpty = fields.Bool(description="No position filled?")

class SolvedBoardSchema(Schema):
    board = fields.List(
        fields.Integer(validate=validate.Range(min=0,  max=9)),
        validate=validate.Length(81, 81)
    )

class BoardSolutionsSchema(Schema):
    solve_time = fields.Float(
        description="Elapsed time, in seconds, for finding all solutions.",
    )
    solved_boards = fields.List(
        fields.Nested(SolvedBoardSchema), 
    )
    status = fields.String(
        description='One of the py-sudoku.SolverStatus values.',
    )

class GeneratedBoardSchema(Schema):
    board = fields.List(
        fields.Nested(SolvedBoardSchema), 
    )
    gen_time = fields.Float(
        description="Elapsed time, in seconds, for generating the board.",
    )
    status = fields.String(
        description='One of the py-sudoku.GeneratorStatus values.',
    )
