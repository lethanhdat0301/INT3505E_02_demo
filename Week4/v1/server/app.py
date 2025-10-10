from flask import Flask, jsonify, request
from data import books, borrow_records
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)


@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    new_book['id'] = len(books) + 1
    books.append(new_book)
    return jsonify({'message': 'Book added successfully', 'book': new_book}), 201

@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    book_id = data.get('book_id')
    user = data.get('user')

    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if book['available'] == False:
        return jsonify({'error': 'Book already borrowed'}), 400

    book['available'] = False
    borrow_records.append({'book_id': book_id, 'user': user})
    return jsonify({'message': f'{user} borrowed "{book["title"]}" successfully'})


@app.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()
    book_id = data.get('book_id')
    user = data.get('user')

    record = next((r for r in borrow_records if r['book_id'] == book_id and r['user'] == user), None)
    if not record:
        return jsonify({'error': 'No record found'}), 404

    book = next((b for b in books if b['id'] == book_id), None)
    book['available'] = True
    borrow_records.remove(record)

    return jsonify({'message': f'{user} returned "{book["title"]}" successfully'})


@app.route('/records', methods=['GET'])
def get_records():
    return jsonify(borrow_records)

if __name__ == '__main__':
    app.run(debug=True)
