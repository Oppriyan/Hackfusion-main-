from functools import wraps
from flask import request, jsonify
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")


def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({
                    "status": "error",
                    "code": "missing_token",
                    "message": "Authorization token required"
                }), 401

            try:
                token = auth_header.split(" ")[1]  # Expect: Bearer <token>
                decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                if decoded.get("role") != required_role:
                    return jsonify({
                        "status": "error",
                        "code": "forbidden",
                        "message": "Insufficient permissions"
                    }), 403

            except Exception:
                return jsonify({
                    "status": "error",
                    "code": "invalid_token",
                    "message": "Invalid or expired token"
                }), 401

            return f(*args, **kwargs)

        return wrapper
    return decorator