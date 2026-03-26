from flask import Blueprint 

plans_bp = Blueprint("plans_bp", __name__)

from . import routes 