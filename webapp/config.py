import os
from redis import StrictRedis

class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=os.environ.get('REDIS_HOST'), db=0)
    PERMANENT_SESSION_LIFETIME = 600
    CACHE_REDIS = StrictRedis(host=os.environ.get('REDIS_HOST'), db=1)
    CACHE_REDIS_DEFAULT_TIMEOUT = 3600


