from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
import os
import logging
from flask.ext.cors import CORS
import config

db = None

def setup_app(app):
    global db

    # load config
    app.config.from_object('dancar.config.DevelopmentConfig')
    # put local instance configuration in here
    app.config.from_pyfile('local.cfg', silent=True)

    db = SQLAlchemy(app)

    if os.getenv('SQL'):
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # logging.getLogger('flask_cors').setLevel(logging.DEBUG)

    # CORS
    resources = [ r"/api/.*", r"/oauth/.*" ]
    if app.config.get('CORS_ENABLED'):
        origins = app.config.get('CORS_ORIGINS')
        if origins:
            origins = origins.split(" ")
            CORS(app, resources=resources, origins=origins, supports_credentials=True)
        else:
            CORS(app, resources=resources, origins="*")

def setup_users(app):
    global db

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
                mobile = '+1 510 555-5555',
                password = app.user_manager.hash_password('test'),
                reset_password_token = 'resettoken'
            )
            db.session.add(test_user)
            db.session.commit()
            print " * You can log in with test@test.com/test"

