import jwt
from functools import wraps
from flask import request, jsonify

from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.path in ['/login', '/signup']:
            return f(*args, **kwargs)

        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] 

        if not token:
            return jsonify({"error": "Token is missing!"}), 403

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated
