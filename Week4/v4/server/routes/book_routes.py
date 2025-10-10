from flask import Blueprint, request, jsonify
from utils.jwt_helper import verify_token
from utils.cache_helper import cache_response
from database import books

book_bp = Blueprint("books_v4", __name__)

def get_user_from_header():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return verify_token(token)

@book_bp.route("/", methods=["GET"])
def get_books():
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401
    
    return cache_response(books, max_age=120)

@book_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    for book in books:
        if book["id"] == book_id:
            return cache_response(book, max_age=300)
    return jsonify({"message": "Book not found"}), 404
