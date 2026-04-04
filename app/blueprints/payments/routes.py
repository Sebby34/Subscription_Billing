from app.blueprints.payments import payments_bp
from app.blueprints.payments.schemas import payment_schema, payments_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Payment, db, User 
from sqlalchemy import select 
from app.extensions import limiter, cache
from app.utils.util import token_required  


@payments_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
@token_required
def create_payment(user_id): 
    try: 
        new_payment = payment_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    new_payment.user_id = user_id

    db.session.add(new_payment)
    db.session.commit()

    return payment_schema.jsonify(new_payment), 201

@payments_bp.route("/", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_payments(user_id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role != "admin": 
        return jsonify({"message": "Admin only"}), 403

    query = select(Payment)
    payments = db.session.execute(query).scalars().all()

    return payments_schema.jsonify(payments), 200

@payments_bp.route("/<int:id>", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_payment(user_id, id): 
    payment = db.session.get(Payment, id)

    if not payment: 
        return jsonify({"message": "Invalid payment id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role != "admin" and payment.user_id != int(user_id): 
        return jsonify({"message": "Unauthorized access"}), 403
    
    return payment_schema.jsonify(payment), 200