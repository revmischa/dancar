import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    if os.environ.has_key('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/dancar'


class TestingConfig(Config):
    TESTING = True
