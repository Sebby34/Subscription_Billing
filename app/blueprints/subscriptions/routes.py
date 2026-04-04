from app.blueprints.subscriptions import subscriptions_bp
from app.blueprints.subscriptions.schemas import subscription_schema, subscriptions_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Subscription, db, User 
from sqlalchemy import select 
from app.extensions import limiter 
from app.utils.util import token_required


@subscriptions_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
@token_required
def create_subscription(user_id): 
    try: 
        new_subscription = subscription_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
   
    new_subscription.user_id = user_id
    
    db.session.add(new_subscription)
    db.session.commit()

    return subscription_schema.jsonify(new_subscription), 201

@subscriptions_bp.route("/", methods = ["GET"])
@token_required
def get_subscriptions(user_id): 
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin": 
        return jsonify({"message": "Unauthorized access"}), 403

    query = select(Subscription)
    subscriptions = db.session.execute(query).scalars().all()

    return subscriptions_schema.jsonify(subscriptions), 200

@subscriptions_bp.route("/<int:id>", methods = ["GET"])
@token_required
def get_subscription(user_id, id): 
    subscription = db.session.get(Subscription, id)

    if not subscription: 
        return jsonify({"message": "Invalid subscription id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin" and subscription.user_id != int(user_id): 
        return jsonify({"message": "Unauthorized access"}), 403
    
    return subscription_schema.jsonify(subscription), 200

@subscriptions_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("10 per minute")
@token_required
def update_subscription(user_id, id): 
    subscription = db.session.get(Subscription, id)
    if not subscription: 
        return jsonify({"error": "Invalid subscription id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin" and subscription.user_id != int(user_id): 
        return jsonify({"message": "Unauthorized update"}), 403

    try: 
        updated_subscription = subscription_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    subscription.status = updated_subscription.status
    subscription.start_date = updated_subscription.start_date
    subscription.plan_id = updated_subscription.plan_id

    db.session.commit()
    return subscription_schema.jsonify(subscription), 200

@subscriptions_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("5 per minute")
@token_required
def delete_subscription(user_id, id): 
    subscription = db.session.get(Subscription, id)

    if not subscription: 
        return jsonify({"message": "Invalid subscription id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin" and subscription.user_id != int(user_id): 
        return jsonify({"message": "Unauthorized deletion"}), 403
    
    db.session.delete(subscription)
    db.session.commit()
    return jsonify({"message": f'successfully deleted subscription {id}'}), 200