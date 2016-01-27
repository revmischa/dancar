import os

# base settings
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    CORS_ENABLED = True
    CORS_ORIGINS = 'http://localhost:5000'
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_ONYX_URL', 'postgresql:///dancar')
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    USER_ENABLE_USERNAME = False
    USER_ENABLE_CHANGE_USERNAME = False
    USER_ENABLE_LOGIN_WITHOUT_CONFIRM = True
    USER_ENABLE_CONFIRM_EMAIL = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
