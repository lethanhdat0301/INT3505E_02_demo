# models.py

class Book:
    def __init__(self, id, title, author, available=True):
        self.id = id
        self.title = title
        self.author = author
        self.available = available

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "available": self.available
        }

class BorrowRecord:
    def __init__(self, user, book_id):
        self.user = user
        self.book_id = book_id

    def to_dict(self):
        return {"user": self.user, "book_id": self.book_id}
