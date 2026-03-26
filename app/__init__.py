from flask import Flask 
from app.models import db 
from app.extensions import ma, limiter, cache   
from app.blueprints.users import users_bp
from app.blueprints.plans import plans_bp 
from app.blueprints.subscriptions import subscriptions_bp
from app.blueprints.payments import payments_bp 
from app.blueprints.invoices import invoices_bp 


def create_app(config_name): 
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(users_bp, url_prefix = "/users")
    app.register_blueprint(plans_bp, url_prefix = "/plans")
    app.register_blueprint(subscriptions_bp, url_prefix = "/subscriptions")
    app.register_blueprint(payments_bp, url_prefix = "/payments")
    app.register_blueprint(invoices_bp, url_prefix = "/invoices")

    return app 