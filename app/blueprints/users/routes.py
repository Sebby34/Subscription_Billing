from app.blueprints.users import users_bp
from app.blueprints.users.schemas import user_schema, users_schema, login_schema 
from flask import request, jsonify 
from marshmallow import ValidationError
from app.models import User, db 
from sqlalchemy import select 
from app.extensions import limiter, cache  
from app.utils.util import encode_token, token_required


@users_bp.route("/login", methods = ["POST"])
def login(): 
    try: 
        credentials = login_schema.load(request.json)
        email = credentials["email"]
        password = credentials["password"]
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    query = select(User).where(User.email == email)
    user = db.session.execute(query).scalars().first()

    if user and user.password == password: 
        token = encode_token(user.id)

        response = {
            "status": "success",
            "message": "successfully logged in", 
            "token": token 
        }
        return jsonify(response), 200
    else: 
        return jsonify({"message": "Invalid email or password!"}), 404

@users_bp.route("/", methods = ["POST"])
@limiter.limit("10 per minute")
def create_user(): 
    try: 
        user_data = user_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400

    new_user = User(name = user_data["name"], email = user_data["email"], password = user_data["password"], role = user_data["role"])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201

@users_bp.route("/", methods = ["GET"])
@token_required 
@cache.cached(timeout = 60, query_string = True)
def get_users(user_id): 
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin": 
        return jsonify({"message": "Unauthorized access"}), 403
    
    try: 
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(User)
        users = db.paginate(query, page = page, per_page = per_page)
        return users_schema.jsonify(users), 200
    
    except Exception as e: 
        query = select(User)
        users = db.session.execute(query).scalars().all()

        return users_schema.jsonify(users), 200

@users_bp.route("/<int:id>", methods = ["GET"])
@token_required
@cache.cached(timeout = 60)
def get_user(user_id, id): 
    user = db.session.get(User, id)

    if not user: 
        return jsonify({"message": "Invalid user id"}), 404
    
    current_user = db.session.get(User, user_id)
    if current_user.role.lower() != "admin" and user_id != id: 
        return jsonify({"message": "Unauthorized access"}), 403
    
    return user_schema.jsonify(user), 200

@users_bp.route("/<int:id>", methods = ["PUT"])
@limiter.limit("20 per minute")
@token_required
def update_user(user_id, id): 
    user = db.session.get(User, id)

    if not user: 
        return jsonify({"message": "Invalid user id"}), 404
    
    current_user = db.session.get(User, user_id)

    if current_user.role.lower() != "admin" and user_id != id: 
        return jsonify({"message": "Unauthorized update"}), 403
    
    try: 
        user_data = user_schema.load(request.json, partial = True)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    if "name" in user_data: 
        user.name = user_data["name"]
    if "email" in user_data: 
        user.email = user_data["email"]
    if "password" in user_data: 
        user.password = user_data["password"]
    if "role" in user_data: 
        user.role = user_data["role"]

    db.session.commit()
    return user_schema.jsonify(user), 200

@users_bp.route("/<int:id>", methods = ["DELETE"])
@limiter.limit("10 per minute")
@token_required
def delete_user(user_id, id): 
    user_to_delete = db.session.get(User, id)
    current_user = db.session.get(User, user_id)

    if not user_to_delete: 
        return jsonify({"message": "Invalid user id"}), 404
    
    if current_user.role.lower() != "admin" and user_to_delete.id != user_id: 
        return jsonify({"message": "Unauthorized deletion"}), 403
    
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify({"message": f'successfully deleted user {id}'}), 200