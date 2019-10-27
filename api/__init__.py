from flask import Blueprint

rest_api = Blueprint('api', __name__)

class InvalidUsage(Exception):
    """Custom exception to be raised by API in case of errors."""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# Expose the resources in the api to the runner Flask App.
# Note: The import below must come after the definition of
#       object rest_api, as the resource definition files
#       make use of rest_api and of InvalidUsage. 
from . import board, solved_board
