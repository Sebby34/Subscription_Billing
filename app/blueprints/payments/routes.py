from app.blueprints.payments import payments_bp
from app.blueprints.payments.schemas import payment_schema, payments_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Payment, db 
from sqlalchemy import select 
from app.extensions import limiter, cache  


@payments_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
def create_payment(): 
    try: 
        new_payment = payment_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    db.session.add(new_payment)
    db.session.commit()

    return payment_schema.jsonify(new_payment), 201

@payments_bp.route("/", methods = ["GET"])
@cache.cached(timeout = 60)
def get_payments(): 
    query = select(Payment)
    payments = db.session.execute(query).scalars().all()

    return payments_schema.jsonify(payments), 200

@payments_bp.route("/<int:id>", methods = ["GET"])
@cache.cached(timeout = 60)
def get_payment(id): 
    payment = db.session.get(Payment, id)

    if not payment: 
        return jsonify({"message": "Invalid payment id"}), 404
    
    return payment_schema.jsonify(payment), 200