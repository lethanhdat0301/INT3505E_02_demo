from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy import or_
from models import BorrowRecord, User, Book
from database import db
from utils.pagination import PaginationHelper, handle_pagination_error
from utils.jwt_helper import jwt_required

borrows_bp = Blueprint('borrows', __name__)

@borrows_bp.route('/api/v1/borrows', methods=['GET'])
@swag_from({
    'tags': ['Borrow Records'],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10},
        {'name': 'search', 'in': 'query', 'type': 'string', 'description': 'Tìm theo tên người hoặc sách'},
        {'name': 'is_returned', 'in': 'query', 'type': 'boolean', 'description': 'true/false'},
        {'name': 'sort_by', 'in': 'query', 'type': 'string', 'default': 'borrow_date'},
        {'name': 'order', 'in': 'query', 'type': 'string', 'enum': ['asc', 'desc'], 'default': 'desc'}
    ],
    'responses': {
        200: {
            'description': 'Danh sách phiếu mượn',
            'examples': {
                'application/json': {
                    "data": {
                        "items": [
                            {
                                "id": 1,
                                "user": "John Doe",
                                "book": "Python 101",
                                "borrow_date": "2023-01-01T00:00:00",
                                "return_date": None,
                                "is_returned": False
                            }
                        ],
                        "pagination": {
                            "current_page": 1,
                            "per_page": 10,
                            "total_items": 1,
                            "total_pages": 1,
                            "has_prev": False,
                            "has_next": False
                        }
                    },
                    "meta": {
                        "status": "success",
                        "message": "Showing 1-1 of 1 items"
                    }
                }
            }
        },
        400: {'description': 'Tham số không hợp lệ'}
    }
})
def get_borrow_records():
    # Create pagination helper from request
    pagination_helper = PaginationHelper.from_request(
        max_per_page=50,
        endpoint='borrows.get_borrow_records'
    )
    
    # Validate pagination parameters
    validation_error = pagination_helper.validate_page_params()
    if validation_error:
        return handle_pagination_error(validation_error)
    
    # Get other query parameters
    search = request.args.get('search', type=str)
    is_returned = request.args.get('is_returned', type=str)
    sort_by = request.args.get('sort_by', 'borrow_date', type=str)
    order = request.args.get('order', 'desc', type=str)

    query = BorrowRecord.query.join(User).join(Book)

    # Tìm kiếm (theo tên sách hoặc người mượn)
    if search:
        query = query.filter(or_(
            User.name.ilike(f"%{search}%"),
            Book.title.ilike(f"%{search}%")
        ))

    # Lọc trạng thái trả
    if is_returned:
        query = query.filter(BorrowRecord.is_returned == (is_returned.lower() == 'true'))

    # Sắp xếp
    valid_sort_fields = ['borrow_date', 'return_date', 'id']
    if sort_by not in valid_sort_fields:
        sort_by = 'borrow_date'
        
    sort_column = getattr(BorrowRecord, sort_by, BorrowRecord.borrow_date)
    if order == 'desc':
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Apply pagination and return response
    result = pagination_helper.paginate_query(query)
    
    # Add filter info to meta
    if search or is_returned:
        filters_applied = []
        if search:
            filters_applied.append(f"search: '{search}'")
        if is_returned:
            filters_applied.append(f"returned: {is_returned}")
        
        result["meta"]["filters"] = filters_applied
    
    return jsonify(result), 200


@borrows_bp.route('/api/v1/borrows', methods=['POST'])
@jwt_required
@swag_from({
    'tags': ['Borrow Records'],
    'parameters': [
        {
            'name': 'borrow',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'description': 'ID người mượn'},
                    'book_id': {'type': 'integer', 'description': 'ID sách mượn'}
                },
                'required': ['user_id', 'book_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Tạo phiếu mượn thành công',
            'examples': {
                'application/json': {
                    "id": 1,
                    "user": "John Doe",
                    "book": "Python 101",
                    "borrow_date": "2023-01-01T00:00:00",
                    "return_date": None,
                    "is_returned": False
                }
            }
        },
        400: {'description': 'Dữ liệu không hợp lệ'},
        404: {'description': 'Người dùng hoặc sách không tồn tại'},
        409: {'description': 'Sách đã được mượn'}
    }
})
def create_borrow_record():
    from datetime import datetime
    
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id') or not data.get('book_id'):
            return jsonify({"error": "user_id và book_id là bắt buộc"}), 400
        
        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "Người dùng không tồn tại"}), 404
        
        # Check if book exists
        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({"error": "Sách không tồn tại"}), 404
        
        # Check if book is available
        if not book.is_available:
            return jsonify({"error": "Sách đã được mượn"}), 409
        
        # Create borrow record
        borrow_record = BorrowRecord(
            user_id=data['user_id'],
            book_id=data['book_id'],
            borrow_date=datetime.utcnow()
        )
        
        # Update book availability
        book.is_available = False
        
        db.session.add(borrow_record)
        db.session.commit()
        
        return jsonify(borrow_record.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@borrows_bp.route('/api/v1/borrows/<int:borrow_id>/return', methods=['PUT'])
@swag_from({
    'tags': ['Borrow Records'],
    'parameters': [
        {'name': 'borrow_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'ID phiếu mượn'}
    ],
    'responses': {
        200: {
            'description': 'Trả sách thành công',
            'examples': {
                'application/json': {
                    "id": 1,
                    "user": "John Doe",
                    "book": "Python 101",
                    "borrow_date": "2023-01-01T00:00:00",
                    "return_date": "2023-01-15T00:00:00",
                    "is_returned": True
                }
            }
        },
        404: {'description': 'Phiếu mượn không tồn tại'},
        409: {'description': 'Sách đã được trả'}
    }
})
def return_book(borrow_id):
    from datetime import datetime
    
    try:
        borrow_record = BorrowRecord.query.get(borrow_id)
        if not borrow_record:
            return jsonify({"error": "Phiếu mượn không tồn tại"}), 404
        
        if borrow_record.is_returned:
            return jsonify({"error": "Sách đã được trả"}), 409
        
        # Update borrow record
        borrow_record.return_date = datetime.utcnow()
        borrow_record.is_returned = True
        
        # Update book availability
        book = Book.query.get(borrow_record.book_id)
        book.is_available = True
        
        db.session.commit()
        
        return jsonify(borrow_record.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
