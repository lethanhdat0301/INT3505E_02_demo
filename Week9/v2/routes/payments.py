from flask import Blueprint, request, jsonify
from datetime import datetime
from models import Payment
from database import db
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


@payment_bp.route("/api/v2/payments", methods=["POST"])
@jwt_required
def create_payment_v2():
    idem_key = request.headers.get("Idempotency-Key")
    data = request.get_json() or {}
    print("DEBUG JSON:", data)

    required_fields = ["book_id", "amount", "currency", "payment_method"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "bad_request", "message": "Missing required fields"}), 400
    
    current_user_id = getattr(request, "user_identity", None)
    if not current_user_id:
        return jsonify({"error": "unauthorized", "message": "User identity missing from token"}), 401

    new_payment = Payment (
        user_id=current_user_id,
        book_id=data["book_id"],
        amount=data["amount"],
        currency=data["currency"],
        status="succeeded",
        payment_method=data["payment_method"],
        created_at=datetime.utcnow(),
    )
    
    db.session.add(new_payment)
    db.session.commit()

    if idem_key:
        print(f"[Idempotency] Saved key: {idem_key}")

    return jsonify(new_payment.to_dict()), 201


@payment_bp.route("/api/v2/payments/<int:payment_id>", methods=["GET"])
@jwt_required
def get_payment_status_v2(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"error": "not_found", "message": "Payment not found"}), 404
    
    result = {
        "id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency,
        "user": {"id": payment.user_id},
        "book": {"id": payment.book_id},
        "created_at": payment.created_at.isoformat() + "Z",
    }
    {
}
    return jsonify(result), 200
    