from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy import or_
from models import User
from database import db
from utils.pagination import PaginationHelper, handle_pagination_error

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/v1/users', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10},
        {'name': 'search', 'in': 'query', 'type': 'string', 'description': 'Tìm theo tên hoặc email'},
        {'name': 'sort_by', 'in': 'query', 'type': 'string', 'default': 'name'},
        {'name': 'order', 'in': 'query', 'type': 'string', 'enum': ['asc', 'desc'], 'default': 'asc'}
    ],
    'responses': {
        200: {
            'description': 'Lấy danh sách người dùng thành công',
            'examples': {
                'application/json': {
                    "data": {
                        "items": [
                            {"id": 1, "name": "A", "email": "abc@example.com"},
                            {"id": 2, "name": "B", "email": "xyz@example.com"}
                        ],
                        "pagination": {
                            "current_page": 1,
                            "per_page": 10,
                            "total_items": 2,
                            "total_pages": 1,
                            "has_prev": False,
                            "has_next": False,
                            "prev_page": None,
                            "next_page": None
                        }
                    },
                    "meta": {
                        "status": "success",
                        "message": "Showing 1-2 of 2 items"
                    }
                }
            }
        },
        400: {'description': 'Tham số không hợp lệ'},
        500: {'description': 'Lỗi máy chủ nội bộ'}
    }
})
def get_users():
    try:
        # Create pagination helper from request
        pagination_helper = PaginationHelper.from_request(
            max_per_page=50,
            endpoint='users.get_users'
        )
        
        # Validate pagination parameters
        validation_error = pagination_helper.validate_page_params()
        if validation_error:
            return handle_pagination_error(validation_error)
        
        # Get other query parameters
        search = request.args.get('search', type=str)
        sort_by = request.args.get('sort_by', 'name', type=str)
        order = request.args.get('order', 'asc', type=str)
        exact = request.args.get('exact', 'false').lower() == 'true'

        query = User.query

        # Search functionality
        if search:
            if exact:
                query = query.filter(
                    or_(
                        User.name.ilike(search),
                        User.email.ilike(search)
                    )
                )
            else:
                query = query.filter(
                    or_(
                        User.name.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%")
                    )
                )

        # Sorting
        valid_sort_fields = ['name', 'email', 'id']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
            
        sort_column = getattr(User, sort_by, User.name)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

        # Apply pagination and return response
        result = pagination_helper.paginate_query(query)
        
        # Add search info to meta if search was applied
        if search:
            result["meta"]["search"] = {
                "query": search,
                "exact_match": exact
            }
        
        return jsonify(result), 200

    except Exception as e:
        print(e)
        return jsonify({
            "meta": {
                "status": "error",
                "message": "Đã xảy ra lỗi khi xử lý yêu cầu"
            },
            "error": str(e)
        }), 500


@users_bp.route('/api/v1/users', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Tên người dùng'},
                    'email': {'type': 'string', 'description': 'Email người dùng'}
                },
                'required': ['name', 'email']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Tạo người dùng thành công',
            'examples': {
                'application/json': {
                    "status": "success",
                    "message": "Tạo người dùng thành công",
                    "data": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john@example.com"
                    }
                }
            }
        },
        400: {'description': 'Dữ liệu không hợp lệ'},
        409: {'description': 'Email đã tồn tại'}
    }
})
def create_user():
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({
                "status": "error",
                "message": "Name và email là bắt buộc"
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                "status": "error",
                "message": "Email đã tồn tại"
            }), 409
        
        user = User(
            name=data['name'],
            email=data['email']
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Tạo người dùng thành công",
            "data": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Đã xảy ra lỗi khi tạo người dùng",
            "error": str(e)
        }), 500
