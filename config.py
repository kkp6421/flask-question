import os
from datetime import timedelta
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
        'sqlite:///'+os.path.join(base_dir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
        'sqlite:///'+os.path.join(base_dir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
        'sqlite:///'+os.path.join(base_dir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
