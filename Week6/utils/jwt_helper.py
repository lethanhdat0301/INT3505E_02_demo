import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

def create_access_token(identity, expires_delta: timedelta | None = None) -> str:
    secret = current_app.config.get('JWT_SECRET_KEY', 'abcxyz!@#123')
    now = datetime.utcnow()
    if expires_delta is None:
        expires_delta = timedelta(hours=2)

    payload = {
        'sub': identity,
        'iat': now,
        'exp': now + expires_delta
    }

    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def decode_token(token: str):
    secret = current_app.config.get('JWT_SECRET_KEY', 'abcxyz!@#123')
    return jwt.decode(token, secret, algorithms=['HS256'])

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return jsonify({'message': 'Authorization header is missing!'}), 401
        
        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'message': 'Invalid authorization header format!'}), 401
        
        token = parts[1]
        try:
            payload = decode_token(token)
            request.user_identity = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    return decorated

jwt_required = jwt_required