from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
import os
import logging

app = Flask(__name__)

# load config
app.config.from_object('dancar.config.DevelopmentConfig')

# load database
db = SQLAlchemy(app)

if os.getenv('SQL'):
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


# load routes
import dancar.views

# WebSocket support (not really working atm)
#from flask_sockets import Sockets
#sockets = Sockets(app)

# Flask-User
from dancar.models import User
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

# load up dev sample data
if app.config.get('DEVELOPMENT'):
    if not len(User.query.all()):
        print " * New development environment detected. Adding test user account..."
        test_user = User(
            active = True,
            name = "DanH",
            email = "test@test.com",
            password = app.user_manager.hash_password('test'),
            reset_password_token = 'resettoken'
        )
        db.session.add(test_user)
        db.session.commit()
        print " * You can log in with test@test.com/test"

# Catch error and return back a flask response
# @app.errorhandler(error)
# def catchError(er) :
#     return err.message , err.code , err.headers
