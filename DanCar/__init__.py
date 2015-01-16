from dancar import app, error
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

import dancar.views

app.config.from_object('dancar.config.DevelopmentConfig')
#from flask_sockets import Sockets
#sockets = Sockets(app)

# Catch error and return back a flask response
# @app.errorhandler(error)
# def catchError(er) :
#     return err.message , err.code , err.headers