import os
import bcrypt
from flask import *
from flask_cors import *
from flask_bcrypt import *

#  set up app
app = Flask(__name__)


# index
@app.route('/')
def index():
    return 'hello world'

# run main program
if __name__ == '__main__':
    app.run(debug = True)
