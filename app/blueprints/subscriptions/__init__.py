from flask import Blueprint 

subscriptions_bp = Blueprint("subscriptions_bp", __name__)

from . import routes 