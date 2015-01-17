from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter

app = Flask(__name__)

# load database
db = SQLAlchemy(app)

# load routes
import dancar.views

# load config
app.config.from_object('dancar.config.DevelopmentConfig')

# WebSocket support (not really working atm)
#from flask_sockets import Sockets
#sockets = Sockets(app)

# Flask-User
from dancar.models import User
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

# Catch error and return back a flask response
# @app.errorhandler(error)
# def catchError(er) :
#     return err.message , err.code , err.headers