from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt
import os

from app.models.database import get_db

auth_bp = Blueprint("auth_bp", __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({
            "status": "error",
            "message": "Email and password required"
        }), 400

    email = data["email"]
    password = data["password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, password_hash, role
    FROM users
    WHERE email = ?
""", (email,))

    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401

    token = jwt.encode({
        "user_id": user["id"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=6)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "status": "success",
        "token": token,
        "role": user["role"],
        "name": user["name"],
        "customer_id": user["id"]
    }), 200