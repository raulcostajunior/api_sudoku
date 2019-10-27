from marshmallow import Schema, fields, validate

class BoardSchema(Schema):
    board = fields.List(fields.Integer(validate=validate.Range(min=0,  max=9)))

class BoardFlagsSchema(Schema):
    isValid = fields.Bool()
    isComplete = fields.Bool()
    isEmpty = fields.Bool()