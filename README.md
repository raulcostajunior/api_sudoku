# api_sudoku
A **Python3/Flask** based **api** for generating, managing and solving Sudoku boards.

## Requirements

**api_sudoku** uses [**py-libsudoku**](https://pypi.org/project/py-libsudoku/), a C++ based Python extension. To install the 
**py-libsudoku** requirement, you need a **C++ 11** compliant compiler and 
**CMake** version 3.5 (or newer).

The **api_sudoku** requirements can be installed with:

    pip install -r requirements.txt
    
Development requirements for **api_sudoku** can be installed with:

    pip install -r requirements_dev.txt
    
The **requirements_dev.txt** adds dependencies on **pylint** and on packages used to generate the api documentation - namely  **marshmallow**, **apispec** and **apispec-webframeworks**.

## Running Locally

To run the api using Flask's development server:

    export FLASK_APP=api_runner.py
    export FLASK_DEBUG=1 (optional)
    flask run

The api documentation is browsable from the api root - running locally on Flask's development server with its default port, the api documentation can be accessed at http://127.0.0.1:5000.

<!--
## Demo

The api can be accessed at http://api-sudoku.herokuapp.com. The files **Procfile** and **runtime.txt** are specific to the Heroku deployment. **cmake** had to be added as dependency to **requirements.txt** for the Heroku deployment to work.
-->
