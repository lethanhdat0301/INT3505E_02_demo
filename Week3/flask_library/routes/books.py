from flask import Blueprint, request, jsonify
from database import db
from models import Book

books_bp = Blueprint("books", __name__)

@books_bp.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author": b.author, "available": b.available} for b in books])

@books_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    new_book = Book(title=data["title"], author=data["author"])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added", "id": new_book.id}), 201

@books_bp.route("/books/<int:id>", methods=["PUT"])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    data = request.get_json()
    if "title" in data:
        book.title = data["title"]
    if "author" in data:
        book.author = data["author"]

    db.session.commit()
    return jsonify({"message": "Book updated"})

@books_bp.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})
