#!/usr/bin/env python3
"""
Script to create sample data for the library management system
"""

from app import app
from database import db
from models import Book, User, BorrowRecord
from datetime import datetime

def create_sample_data():
    """Create sample books, users, and borrow records"""
    
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        BorrowRecord.query.delete()
        Book.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("Creating sample books...")
        books = [
            Book(title="Python Programming", author="John Smith", category="Programming"),
            Book(title="Data Science Handbook", author="Sarah Johnson", category="Data Science"),
            Book(title="Web Development with Flask", author="Mike Brown", category="Web Development"),
            Book(title="Machine Learning Basics", author="Emily Davis", category="Machine Learning"),
            Book(title="JavaScript Fundamentals", author="Tom Wilson", category="Programming"),
            Book(title="Database Design", author="Lisa Anderson", category="Database"),
            Book(title="Software Architecture", author="David Miller", category="Software Engineering"),
            Book(title="Clean Code", author="Robert Martin", category="Programming"),
            Book(title="The Pragmatic Programmer", author="Andy Hunt", category="Programming"),
            Book(title="Design Patterns", author="Gang of Four", category="Software Engineering")
        ]
        
        for book in books:
            db.session.add(book)
        db.session.commit()
        print(f"Created {len(books)} books")
        
        print("Creating sample users...")
        users = [
            User(name="Alice Johnson", email="alice@example.com"),
            User(name="Bob Smith", email="bob@example.com"),
            User(name="Charlie Brown", email="charlie@example.com"),
            User(name="Diana Prince", email="diana@example.com"),
            User(name="Edward Norton", email="edward@example.com"),
            User(name="Fiona Green", email="fiona@example.com"),
            User(name="George Lucas", email="george@example.com"),
            User(name="Helen Troy", email="helen@example.com")
        ]
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users")
        
        print("Creating sample borrow records...")
        # Create some borrow records (some returned, some not)
        borrow_records = [
            BorrowRecord(user_id=1, book_id=1, borrow_date=datetime(2023, 1, 1), return_date=datetime(2023, 1, 15), is_returned=True),
            BorrowRecord(user_id=2, book_id=2, borrow_date=datetime(2023, 1, 5), is_returned=False),
            BorrowRecord(user_id=3, book_id=3, borrow_date=datetime(2023, 1, 10), return_date=datetime(2023, 1, 25), is_returned=True),
            BorrowRecord(user_id=4, book_id=4, borrow_date=datetime(2023, 2, 1), is_returned=False),
            BorrowRecord(user_id=5, book_id=5, borrow_date=datetime(2023, 2, 5), return_date=datetime(2023, 2, 20), is_returned=True),
        ]
        
        for record in borrow_records:
            db.session.add(record)
            
        # Update book availability based on borrow records
        borrowed_books = [2, 4]  # Books that are currently borrowed
        for book_id in borrowed_books:
            book = Book.query.get(book_id)
            if book:
                book.is_available = False
        
        db.session.commit()

if __name__ == "__main__":
    create_sample_data()