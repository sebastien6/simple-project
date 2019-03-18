from flask import Blueprint

bp = Blueprint('auth', __name__)

from micro.auth import routes