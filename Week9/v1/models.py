from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120))
    category = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "bookId": self.id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "is_available": self.is_available
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            "userId": self.id,
            "name": self.name,
            "email": self.email
        }
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='borrow_records')
    book = db.relationship('Book', backref='borrow_records')

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.name,
            "book": self.book.title,
            "borrow_date": self.borrow_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "is_returned": self.is_returned
        }
