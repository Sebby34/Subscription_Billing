from app.blueprints.users import users_bp
from app.blueprints.users.schemas import user_schema, users_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import User, db 
from sqlalchemy import select 
from app.extensions import limiter, cache  


@users_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
def create_user(): 
    try: 
        user_data = user_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404

    new_user = User(name = user_data["name"], email = user_data["email"])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201

@users_bp.route("/", methods = ["GET"])
@cache.cached(timeout = 60)
def get_users(): 
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

@users_bp.route("/<int:id>", methods = ["GET"])
@cache.cached(timeout = 60)
def get_user(id): 
    user = db.session.get(User, id)

    if not user: 
        return jsonify({"message": "Invalid user id"}), 404
    
    return user_schema.jsonify(user), 200

@users_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("20 per minute")
def update_user(id): 
    user = db.session.get(User, id)

    if not user: 
        return jsonify({"message": "Invalid user id"}), 404
    
    try: 
        user_data = user_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 404
    
    user.name = user_data["name"]
    user.email = user_data["email"]

    db.session.commit()
    return user_schema.jsonify(user), 200

@users_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("10 per minute")
def delete_user(id): 
    user = db.session.get(User, id)

    if not user: 
        return jsonify({"message": "Invalid user id"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f'successfully deleted user {id}'}), 200