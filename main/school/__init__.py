
from flask import Blueprint

bp = Blueprint("school", __name__, url_prefix="/school")

from . import views