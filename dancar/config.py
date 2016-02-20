import os

# base settings
class Config(object):
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    CORS_ENABLED = True
    CORS_ORIGINS = 'http://localhost:5000 http://localhost:9000 http://localhost:8100'
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_ONYX_URL', 'postgresql:///dancar')
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    USER_ENABLE_USERNAME = False
    USER_ENABLE_CHANGE_USERNAME = False
    USER_ENABLE_LOGIN_WITHOUT_CONFIRM = True
    USER_ENABLE_CONFIRM_EMAIL = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', '1286138911412007') # dancar-dev
    FACEBOOK_SECRET = os.getenv('FACEBOOK_SECRET', '29cebc4f7867226222fa9a4e963345e1') # dancar-dev

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
