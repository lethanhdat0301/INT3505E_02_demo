from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

books = [
    {"id": 1, "title": "Python 101", "user_id": 1},
    {"id": 2, "title": "Flask in Action", "user_id": 2},
]

USER_SERVICE_URL = "http://localhost:5001/users/"

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    try:
        r = requests.get(USER_SERVICE_URL + str(book["user_id"]))
        user = r.json()
        book["user"] = user
    except Exception as e:
        return jsonify({"error": f"Cannot reach UserService: {str(e)}"}), 500

    return jsonify(book)

if __name__ == "__main__":
    app.run(port=5000)
