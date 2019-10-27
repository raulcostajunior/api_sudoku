from flask import Blueprint

rest_api = Blueprint('api', __name__)

# Expose the resources in the api to the runner Flask App.
# Note: The import below must come after the definition of
#       object rest_api, as the resource definition files
#       make use of rest_api. 
from . import board, solved_board