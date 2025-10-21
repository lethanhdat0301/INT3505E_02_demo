from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    borrows = db.relationship("Borrow", back_populates="user")

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    borrows = db.relationship("Borrow", back_populates="book")

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))

    user = db.relationship("User", back_populates="borrows")
    book = db.relationship("Book", back_populates="borrows")
