from app.blueprints.plans import plans_bp 
from app.blueprints.plans.schemas import plan_schema, plans_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Plan, db 
from sqlalchemy import select 
from app.extensions import limiter, cache 


@plans_bp.route("/", methods = ["POST"])
@limiter.limit("5 per minute")
def create_plan(): 
    try: 
        plan_data = plan_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404

    new_plan = Plan(name = plan_data["name"], price = plan_data["price"], 
                    billing_cycle = plan_data["billing_cycle"])
    db.session.add(new_plan)
    db.session.commit()

    return plan_schema.jsonify(new_plan), 201

@plans_bp.route("/", methods = ["GET"])
@cache.cached(timeout = 60)
def get_plans(): 
    query = select(Plan)
    plans = db.session.execute(query).scalars().all()

    return plans_schema.jsonify(plans), 200

@plans_bp.route("/<int:id>", methods = ["GET"])
@cache.cached(timeout = 60)
def get_plan(id): 
    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    return plan_schema.jsonify(plan), 200

@plans_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("10 per minute")
def update_plan(id): 
    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    try: 
        plan_data = plan_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    
    plan.name = plan_data["name"]
    plan.price = plan_data["price"]
    plan.billing_cycle = plan_data["billing_cycle"]

    db.session.commit()
    return plan_schema.jsonify(plan), 200

@plans_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("5 per minute")
def delete_plan(id): 
    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    db.session.delete(plan)
    db.session.commit()
    return jsonify({"message": f'successfully deleted plan {id}'}), 200