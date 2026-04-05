from app.blueprints.plans import plans_bp 
from app.blueprints.plans.schemas import plan_schema, plans_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import Plan, db, User 
from sqlalchemy import select 
from app.extensions import limiter, cache 
from app.utils.util import token_required


@plans_bp.route("/", methods = ["POST"])
@limiter.limit("5 per minute")
@token_required 
def create_plan(user_id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role.lower() != "admin": 
        return jsonify({"message": "Admin only"}), 403
    
    try: 
        plan_data = plan_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400

    new_plan = Plan(name = plan_data["name"], price = plan_data["price"], 
                    billing_cycle = plan_data["billing_cycle"])
    db.session.add(new_plan)
    db.session.commit()

    return plan_schema.jsonify(new_plan), 201

@plans_bp.route("/", methods = ["GET"])
@token_required
@cache.cached(timeout = 60, query_string = True)
def get_plans(user_id): 
    try: 
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(Plan)
        plans = db.paginate(query, page = page, per_page = per_page)
        return plans_schema.jsonify(plans), 200
    
    except Exception as e: 
        query = select(Plan)
        plans = db.session.execute(query).scalars().all()

        return plans_schema.jsonify(plans), 200

@plans_bp.route("/<int:id>", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_plan(user_id, id): 
    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    return plan_schema.jsonify(plan), 200

@plans_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("10 per minute")
@token_required
def update_plan(user_id, id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role.lower() != "admin": 
        return jsonify({"message": "Admin only"}), 403

    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    try: 
        plan_data = plan_schema.load(request.json, partial = True)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    if "name" in plan_data: 
        plan.name = plan_data["name"]
    if "price" in plan_data:
        plan.price = plan_data["price"]
    if "billing_cycle" in plan_data:
        plan.billing_cycle = plan_data["billing_cycle"]

    db.session.commit()
    return plan_schema.jsonify(plan), 200

@plans_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("5 per minute")
@token_required
def delete_plan(user_id, id): 
    current_user = db.session.get(User, user_id)
    
    if current_user.role.lower() != "admin": 
        return jsonify({"message": "Admin only"}), 403

    plan = db.session.get(Plan, id)

    if not plan: 
        return jsonify({"message": "Invalid plan id"}), 404
    
    db.session.delete(plan)
    db.session.commit()
    return jsonify({"message": f'successfully deleted plan {id}'}), 200