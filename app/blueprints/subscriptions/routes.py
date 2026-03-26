from app.blueprints.subscriptions import subscriptions_bp
from app.blueprints.subscriptions.schemas import subscription_schema, subscriptions_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Subscription, db 
from sqlalchemy import select 
from app.extensions import limiter 


@subscriptions_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
def create_subscription(): 
    try: 
        new_subscription = subscription_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    db.session.add(new_subscription)
    db.session.commit()

    return subscription_schema.jsonify(new_subscription), 201

@subscriptions_bp.route("/", methods = ["GET"])
def get_subscriptions(): 
    query = select(Subscription)
    subscriptions = db.session.execute(query).scalars().all()

    return subscriptions_schema.jsonify(subscriptions), 200

@subscriptions_bp.route("/<int:id>", methods = ["GET"])
def get_subscription(id): 
    subscription = db.session.get(Subscription, id)

    if not subscription: 
        return jsonify({"message": "Invalid subscription id"}), 404
    
    return subscription_schema.jsonify(subscription), 200

@subscriptions_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("10 per minute")
def update_subscription(id): 
    subscription = db.session.get(Subscription, id)
    if not subscription: 
        return {"error": "Invalid subscription id"}, 404
    
    try: 
        updated_subscription = subscription_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    
    subscription.status = updated_subscription.status
    subscription.start_date = updated_subscription.start_date
    subscription.user_id = updated_subscription.user_id
    subscription.plan_id = updated_subscription.plan_id

    db.session.commit()
    return subscription_schema.jsonify(subscription), 200

@subscriptions_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("5 per minute")
def delete_subscription(id): 
    subscription = db.session.get(Subscription, id)

    if not subscription: 
        return jsonify({"message": "Invalid subscription id"}), 404
    
    db.session.delete(subscription)
    db.session.commit()
    return jsonify({"message": f'successfully deleted subscription {id}'}), 200