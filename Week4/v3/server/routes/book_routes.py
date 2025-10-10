from flask import Blueprint, jsonify, request
from utils.jwt_helper import verify_token
from database import books

book_bp = Blueprint("books", __name__)

def get_user_from_header():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return verify_token(token)


# ==== Lấy danh sách tất cả sách ====
@book_bp.route("/", methods=["GET"])
def get_books():
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify(books), 200


# ==== Lấy thông tin 1 sách ====
@book_bp.route("/<int:book_id>/", methods=["GET"])
def get_book(book_id):
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    for book in books:
        if book["id"] == book_id:
            return jsonify(book), 200

    return jsonify({"message": "Book not found"}), 404
