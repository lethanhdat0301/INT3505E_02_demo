from flask import Blueprint, jsonify, request
from utils.jwt_helper import verify_token
from database import books, borrows

borrow_bp = Blueprint("borrow", __name__)

def get_user_from_header():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return verify_token(token)


# ==== Mượn sách ====
@borrow_bp.route("/books/<int:book_id>/borrow/", methods=["POST"])
def borrow_book(book_id):
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    for book in books:
        if book["id"] == book_id:
            if not book["available"]:
                return jsonify({"message": "Book not available"}), 400
            book["available"] = False
            borrows.append({"user": user, "book_id": book_id})
            return jsonify({"message": f"{user} borrowed {book['title']}"}), 200

    return jsonify({"message": "Book not found"}), 404


# ==== Trả sách ====
@borrow_bp.route("/books/<int:book_id>/return/", methods=["POST"])
def return_book(book_id):
    user = get_user_from_header()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    for book in books:
        if book["id"] == book_id:
            book["available"] = True
            borrows[:] = [b for b in borrows if not (b["book_id"] == book_id and b["user"] == user)]
            return jsonify({"message": f"{user} returned {book['title']}"}), 200

    return jsonify({"message": "Book not found"}), 404
