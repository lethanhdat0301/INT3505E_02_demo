from flask import Flask, jsonify, request, url_for
from data import books, borrow_records
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/books', methods=['GET'])
def get_books():
    result = []
    for b in books:
        book_repr = b.copy()
        book_repr['_links'] = {
            "self": url_for('get_book', book_id=b['id'], _external=True),
            "borrow": url_for('borrow_book', book_id=b['id'], _external=True),
            "return": url_for('return_book', book_id=b['id'], _external=True),
        }
        result.append(book_repr)
    return jsonify(result), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    book_detail = book.copy()
    book_detail['_links'] = {
        "self": url_for('get_book', book_id=book_id, _external=True),
        "borrow": url_for('borrow_book', book_id=book_id, _external=True),
        "return": url_for('return_book', book_id=book_id, _external=True),
        "collection": url_for('get_books', _external=True)
    }
    return jsonify(book_detail), 200


@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = {
        "id": len(books) + 1,
        "title": data.get("title"),
        "author": data.get("author"),
        "available": True
    }
    books.append(new_book)

    response = jsonify(new_book)
    response.status_code = 201
    response.headers["Location"] = url_for('get_book', book_id=new_book['id'], _external=True)
    return response


@app.route('/api/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
    user = data.get("user")

    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if not book['available']:
        return jsonify({"error": "Book already borrowed"}), 400

    book['available'] = False
    borrow_records.append({'book_id': book_id, 'user': user})

    response = {
        "message": f"{user} borrowed '{book['title']}' successfully",
        "book": book,
        "_links": {
            "self": url_for('borrow_book', book_id=book_id, _external=True),
            "return": url_for('return_book', book_id=book_id, _external=True),
            "records": url_for('get_records', _external=True)
        }
    }
    return jsonify(response), 200


@app.route('/api/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    data = request.get_json()
    user = data.get("user")

    record = next((r for r in borrow_records if r['book_id'] == book_id and r['user'] == user), None)
    if not record:
        return jsonify({"error": "No record found"}), 404

    book = next((b for b in books if b['id'] == book_id), None)
    book['available'] = True
    borrow_records.remove(record)

    response = {
        "message": f"{user} returned '{book['title']}' successfully",
        "book": book,
        "_links": {
            "self": url_for('return_book', book_id=book_id, _external=True),
            "borrow": url_for('borrow_book', book_id=book_id, _external=True),
            "records": url_for('get_records', _external=True)
        }
    }
    return jsonify(response), 200


@app.route('/api/records', methods=['GET'])
def get_records():
    enriched_records = []
    for record in borrow_records:
        book = next((b for b in books if b['id'] == record['book_id']), None)
        if book:
            enriched_records.append({
                **record,
                "book_title": book["title"],
                "_links": {
                    "book": url_for('get_book', book_id=book['id'], _external=True),
                    "self": url_for('get_records', _external=True)
                }
            })
    return jsonify(enriched_records), 200

if __name__ == '__main__':
    app.run(debug=True)