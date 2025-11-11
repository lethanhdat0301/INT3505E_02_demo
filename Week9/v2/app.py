from flask import Flask
from database import db
from flasgger import Swagger
from routes.books import books_bp
from routes.users import users_bp
from routes.borrows import borrows_bp
from routes.demo_pagination import demo_bp
from routes.auth import auth_bp
from routes.payments import payment_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'abc!@#123'
db.init_app(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # tất cả endpoint
            "model_filter": lambda tag: True,  # tất cả model
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

swagger_template = {
    "info": {
        "title": "Library Management API",
        "description": "RESTful API cho hệ thống thư viện (sách, người dùng, mượn trả)",
        "version": "1.0.0"
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

app.register_blueprint(books_bp)
app.register_blueprint(users_bp)
app.register_blueprint(borrows_bp)
app.register_blueprint(demo_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(payment_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
