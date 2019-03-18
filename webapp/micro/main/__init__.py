from flask import Blueprint

bp = Blueprint('main', __name__)

from micro.main import routes