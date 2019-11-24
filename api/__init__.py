from flask import Blueprint, current_app
from flask_executor import Executor

import threading

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

# The flask-executor that will be lazily instantiated
executor = None
# Lock to guarantee single lazy instantiation of executor
executor_lock = threading.Lock()

def get_executor():
    # Lazy instatiantion of the executor
    global executor
    global executor_lock
    with executor_lock:
        if not executor:
            executor = Executor(current_app)
    return executor


# Expose the resources in the api to the runner Flask App.
# Note: The import below must come at the end of the file
#       as the board and solved_board modules use the objects
#       defined above.
from . import board, solved_board
