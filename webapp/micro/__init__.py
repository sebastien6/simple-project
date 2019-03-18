import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_session import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy


#Create flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure flask session
sess = Session()
sess.init_app(app)

# init SQLalchemy app to manage PostgresSQL relational DB
db = SQLAlchemy(app)

# Configure REDIS caching
cache = Config.CACHE_REDIS
cache_timeout = Config.CACHE_REDIS_DEFAULT_TIMEOUT

# Blueprint registration
from micro.auth import bp as auth_bp
from micro.main import bp as main_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)

# Configure Logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('webapp startup')



from micro import models