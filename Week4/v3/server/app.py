from flask import Flask
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.borrow_routes import borrow_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/v3/auth")
app.register_blueprint(book_bp, url_prefix="/api/v3/books")
app.register_blueprint(borrow_bp, url_prefix="/api/v3")

if __name__ == "__main__":
    app.run(debug=True)
    
