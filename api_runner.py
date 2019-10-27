from flask import Flask, jsonify, make_response
from api import rest_api, InvalidUsage

app = Flask(__name__)
app.register_blueprint(rest_api, url_prefix='/v1')

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Custom error handler for invalid api usage."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def index():
    """Display of api documentation at the root endpoint.
       
       To generate the api documentation, run 'python open_api.py'
       from an environment with all the dependencies in 
       'requirements_dev.txt' fullfilled.
    """
    resp_body = """ <html>
                    <head>
                        <title>py_libsudoku API</title>
                        <meta charset="utf-8"/>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <!-- <style> body { margin: 0; padding: 0; } </style> -->
                    </head>
                    <body>
                        <redoc spec-url='https://raw.githubusercontent.com/raulcostajunior/api_sudoku/master/swagger.json' hide-loading></redoc>
                        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
                    </body>
                    </html> """
    resp = make_response(resp_body, 200)
    return resp

