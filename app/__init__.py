from flask import Flask 
from app.models import db 
from app.extensions import ma, limiter, cache   
from app.blueprints.users import users_bp
from app.blueprints.plans import plans_bp 
from app.blueprints.subscriptions import subscriptions_bp
from app.blueprints.payments import payments_bp 
from app.blueprints.invoices import invoices_bp 
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.yaml"


def create_app(config_name): 
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config = {
            "app_name": "SubscriptionBilling"
        }
    )

    app.register_blueprint(users_bp, url_prefix = "/users")
    app.register_blueprint(plans_bp, url_prefix = "/plans")
    app.register_blueprint(subscriptions_bp, url_prefix = "/subscriptions")
    app.register_blueprint(payments_bp, url_prefix = "/payments")
    app.register_blueprint(invoices_bp, url_prefix = "/invoices")
    app.register_blueprint(swaggerui_blueprint, url_prefix = SWAGGER_URL)

    return app 