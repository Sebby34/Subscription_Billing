from app.blueprints.invoices import invoices_bp
from app.blueprints.invoices.schemas import invoice_schema, invoices_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Invoice, db 
from sqlalchemy import select 
from app.extensions import limiter, cache  


@invoices_bp.route("/", methods = ["POST"])
@limiter.limit("5 per minute")
def create_invoice(): 
    try: 
        new_invoice = invoice_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    db.session.add(new_invoice)
    db.session.commit()

    return invoice_schema.jsonify(new_invoice), 201

@invoices_bp.route("/", methods = ["GET"])
@cache.cached(timeout = 60)
def get_invoices(): 
    query = select(Invoice)
    invoices = db.session.execute(query).scalars().all()

    return invoices_schema.jsonify(invoices), 200

@invoices_bp.route("/<int:id>", methods = ["GET"])
@cache.cached(timeout = 60)
def get_invoice(id): 
    invoice = db.session.get(Invoice, id)

    if not invoice: 
        return jsonify({"message": "Invalid invoice id"}), 404
    
    return invoice_schema.jsonify(invoice), 200