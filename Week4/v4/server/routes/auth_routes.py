# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from utils.jwt_helper import generate_token
from database import users

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"message": "Invalid credentials"}), 401

    token = generate_token(username)
    return jsonify({"token": token}), 200
