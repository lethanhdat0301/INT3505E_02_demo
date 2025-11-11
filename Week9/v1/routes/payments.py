from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

from utils.jwt_helper import jwt_required

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/api/v1/payments/book", methods=["POST"])
def pay_book():
    api_key = request.headers.get("X-API-Key")
    if api_key != "demo_api_key_v1":
        return jsonify({"error": "unauthorized", "message": "Invalid API key"}), 401
    
    data = request.get_json() or {}
    print("DEBUG JSON:", data)
    request_fields = ["bookID", "userID", "amount", "currency", "paymentMethod"]
    if not all(field in data for field in request_fields):
        return jsonify({"error": "bad_request", "message": "Missing required fields"}), 400
    
    transaction_id = f"tx_{uuid.uuid4().hex[:8]}"
    result = {
        "transactionId": transaction_id,
        "status": "succeeded",
        "amount": data["amount"],
        "currency": data["currency"],
        "message": "Payment successful",
    }
    return jsonify(result), 200
