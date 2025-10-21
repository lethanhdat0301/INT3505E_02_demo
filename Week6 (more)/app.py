from flask import Flask, jsonify
from models import db, User, Book, Borrow
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
db.init_app(app)

def setup_data():
    db.drop_all()
    db.create_all()

    books = [Book(title=f"Book {i}") for i in range(1, 6)]
    user = User(name="Alice")
    db.session.add_all(books + [user])
    db.session.commit()

    for b in books:
        db.session.add(Borrow(user_id=user.id, book_id=b.id))
    db.session.commit()

# Naive implementation causing N+1 problem
@app.route("/borrows/v1")
def borrows_v1():
    borrows = Borrow.query.all()
    result = []
    for b in borrows:
        # Each access to b.book triggers a separate query -> N+1 problem
        result.append({"borrow_id": b.id, "book_title": b.book.title})
    return jsonify(result)

# Fixed n+1 problem using joinedload
@app.route("/borrows/v2")
def borrows_v2():
    borrows = Borrow.query.options(joinedload(Borrow.book)).all()
    result = [{"borrow_id": b.id, "book_title": b.book.title} for b in borrows]
    return jsonify(result)

if __name__ == "__main__":
    with app.app_context():
        setup_data()
    app.run(debug=True)
