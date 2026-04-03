from datetime import datetime, timedelta, timezone 
from jose import jwt
from flask import current_app, request, jsonify   
from functools import wraps
import jose 

def encode_token(user_id): 
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days = 0, hours = 1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id)
    }

    secret_key = current_app.config["SECRET_KEY"]
    token = jwt.encode(payload, secret_key, algorithm = "HS256")
    return token 

def token_required(f): 
    @wraps(f)
    def decorated(*args, **kwargs): 
        token = None
        secret_key = current_app.config["SECRET_KEY"]
        if "Authorization" in request.headers: 
            token = request.headers["Authorization"].split(" ")[1]

            if not token: 
                return jsonify({"message": "missing token"}), 401
            
            try: 
                data = jwt.decode(token, secret_key, algorithms = ["HS256"])
                user_id = int(data["sub"])
            
            except jose.exceptions.ExpiredSignatureError as e: 
                return jsonify({"message": "token expired"}), 401
            except jose.exceptions.JWTError: 
                return jsonify({"message": "invalid token"}), 401
            
            return f(user_id, *args, **kwargs)
        
        else: 
            return jsonify({"message": "You must be logged in to access this."}), 401
    
    return decorated 