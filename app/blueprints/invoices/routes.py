from app.blueprints.invoices import invoices_bp
from app.blueprints.invoices.schemas import invoice_schema, invoices_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Invoice, db, User  
from sqlalchemy import select 
from app.extensions import limiter, cache  
from app.utils.util import token_required


@invoices_bp.route("/", methods = ["POST"])
@limiter.limit("5 per minute")
@token_required
def create_invoice(user_id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role != "admin": 
        return jsonify({"message": "Admin only"}), 403
    
    try: 
        new_invoice = invoice_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    db.session.add(new_invoice)
    db.session.commit()

    return invoice_schema.jsonify(new_invoice), 201

@invoices_bp.route("/", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_invoices(user_id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role != "admin": 
        return jsonify({"message": "Admin only"}), 403

    query = select(Invoice)
    invoices = db.session.execute(query).scalars().all()

    return invoices_schema.jsonify(invoices), 200

@invoices_bp.route("/<int:id>", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_invoice(user_id, id): 
    invoice = db.session.get(Invoice, id)

    if not invoice: 
        return jsonify({"message": "Invalid invoice id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role != "admin" and invoice.user_id != int(user_id): 
        return jsonify({"message": "Unauthorized access"}), 403
    
    return invoice_schema.jsonify(invoice), 200