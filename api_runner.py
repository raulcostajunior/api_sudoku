from flask import Flask, make_response
from api import rest_api

app = Flask(__name__)
app.register_blueprint(rest_api, url_prefix='/v1')

@app.route("/")
def index():
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

