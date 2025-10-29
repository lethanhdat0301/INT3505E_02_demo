from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from database import db
from models import User
from utils.jwt_helper import create_access_token, decode_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/v1/auth/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {'name': 'body', 'in': 'body', 'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'email': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'required': ['name', 'email', 'password']
        }}
    ],
    'responses': {201: {'description': 'User created'}, 400: {'description': 'Bad request'}}
})

def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

@auth_bp.route('/api/v1/auth/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {'name': 'body', 'in': 'body', 'schema': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'required': ['email', 'password']
        }}
    ],
    'responses': {200: {'description': 'Login success with token'}, 401: {'description': 'Unauthorized'}}
})

def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401
    
    token = create_access_token(identity=str(user.id))

    return jsonify({'access_token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/api/v1/auth/admin', methods=['GET'])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer <JWT access token>'
        }
    ],
    'responses': {
        200: {
            'description': 'Decoded token payload',
            'examples': {
                'application/json': {
                    'token_payload': {'sub': 2, 'iat': 1600000000, 'exp': 1600003600}
                }
            }
        },
        401: {'description': 'Missing or invalid token'}
    }
})
def admin():
    auth = request.headers.get('Authorization', None)
    if not auth:
        return jsonify({'error': 'Authorization header missing'}), 401

    parts = auth.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify({'error': 'Invalid Authorization header'}), 401

    token = parts[1]
    try:
        payload = decode_token(token)
        # return only non-sensitive claims
        safe_payload = {k: v for k, v in payload.items() if k not in ['pw', 'password', 'secret']}
        return jsonify({'token_payload': safe_payload}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401