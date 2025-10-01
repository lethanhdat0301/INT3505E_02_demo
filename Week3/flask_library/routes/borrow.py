from flask import Blueprint, request, jsonify
from database import db
from models import Book, Borrow
from datetime import datetime

borrow_bp = Blueprint("borrow", __name__)

@borrow_bp.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.get_json()
    if not data or "borrower_name" not in data or "book_id" not in data:
        return jsonify({"error": "Invalid input"}), 400

    book = Book.query.get(data["book_id"])
    if not book or not book.available:
        return jsonify({"error": "Book not available"}), 400

    borrow = Borrow(borrower_name=data["borrower_name"], book_id=book.id)
    book.available = False
    db.session.add(borrow)
    db.session.commit()

    return jsonify({"message": "Book borrowed", "borrow_id": borrow.id}), 201

@borrow_bp.route("/return/<int:borrow_id>", methods=["POST"])
def return_book(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if not borrow or borrow.return_date is not None:
        return jsonify({"error": "Invalid borrow record"}), 400

    borrow.return_date = datetime.utcnow()
    book = Book.query.get(borrow.book_id)
    book.available = True
    db.session.commit()

    return jsonify({"message": "Book returned"})
