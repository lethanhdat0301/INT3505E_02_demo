from flask import Flask
from database import db
from routes.books import books_bp
from routes.borrow import borrow_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Đăng ký blueprint
app.register_blueprint(books_bp)
app.register_blueprint(borrow_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
