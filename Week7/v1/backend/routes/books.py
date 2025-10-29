from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy import or_
from models import Book
from database import db
from utils.pagination import PaginationHelper, handle_pagination_error

books_bp = Blueprint('books', __name__)

@books_bp.route('/api/v1/books', methods=['GET'])
@swag_from({
    'tags': ['Books'],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': 'Trang hiện tại'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10, 'description': 'Số phần tử mỗi trang'},
        {'name': 'search', 'in': 'query', 'type': 'string', 'description': 'Tìm theo tên hoặc tác giả'},
        {'name': 'category', 'in': 'query', 'type': 'string', 'description': 'Lọc theo thể loại'},
        {'name': 'available', 'in': 'query', 'type': 'boolean', 'description': 'true = còn sách, false = đã mượn'},
        {'name': 'sort_by', 'in': 'query', 'type': 'string', 'default': 'title', 'description': 'Trường sắp xếp'},
        {'name': 'order', 'in': 'query', 'type': 'string', 'enum': ['asc', 'desc'], 'default': 'asc', 'description': 'Thứ tự'}
    ],
    'responses': {
        200: {
            'description': 'Danh sách sách có phân trang',
            'examples': {
                'application/json': {
                    "data": {
                        "items": [
                            {"id": 1, "title": "Python 101", "author": "Mike", "category": "Lập trình", "is_available": True}
                        ],
                        "pagination": {
                            "current_page": 1,
                            "per_page": 10,
                            "total_items": 42,
                            "total_pages": 5,
                            "has_prev": False,
                            "has_next": True,
                            "prev_page": None,
                            "next_page": 2,
                            "links": {
                                "first": "/api/v1/books?page=1",
                                "last": "/api/v1/books?page=5",
                                "prev": None,
                                "next": "/api/v1/books?page=2",
                                "self": "/api/v1/books?page=1"
                            }
                        }
                    },
                    "meta": {
                        "status": "success",
                        "message": "Showing 1-10 of 42 items"
                    }
                }
            }
        },
        400: {'description': 'Tham số phân trang không hợp lệ'}
    }
})
def get_books():
    # Create pagination helper from request
    pagination_helper = PaginationHelper.from_request(
        max_per_page=50,  # Maximum 50 books per page
        endpoint='books.get_books'
    )
    
    # Validate pagination parameters
    validation_error = pagination_helper.validate_page_params()
    if validation_error:
        return handle_pagination_error(validation_error)
    
    # Get other query parameters
    search = request.args.get('search', type=str)
    category = request.args.get('category', type=str)
    available = request.args.get('available', type=str)
    sort_by = request.args.get('sort_by', 'title', type=str)
    order = request.args.get('order', 'asc', type=str)

    query = Book.query

    # Tìm kiếm
    if search:
        query = query.filter(or_(
            Book.title.ilike(f"%{search}%"),
            Book.author.ilike(f"%{search}%")
        ))

    # Lọc
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    if available:
        query = query.filter(Book.is_available == (available.lower() == 'true'))

    # Sắp xếp
    valid_sort_fields = ['title', 'author', 'category', 'id']
    if sort_by not in valid_sort_fields:
        sort_by = 'title'
    
    sort_column = getattr(Book, sort_by, Book.title)
    if order == 'desc':
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Apply pagination and return response
    result = pagination_helper.paginate_query(query)
    
    # Add search/filter info to meta
    if search or category or available:
        filters_applied = []
        if search:
            filters_applied.append(f"search: '{search}'")
        if category:
            filters_applied.append(f"category: '{category}'")
        if available:
            filters_applied.append(f"available: {available}")
        
        result["meta"]["filters"] = filters_applied
    
    return jsonify(result), 200


@books_bp.route('/api/v1/books', methods=['POST'])
@swag_from({
    'tags': ['Books'],
    'parameters': [
        {
            'name': 'book',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Tên sách'},
                    'author': {'type': 'string', 'description': 'Tác giả'},
                    'category': {'type': 'string', 'description': 'Thể loại'}
                },
                'required': ['title']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Tạo sách thành công',
            'examples': {
                'application/json': {
                    "id": 1,
                    "title": "Python 101",
                    "author": "Mike",
                    "category": "Lập trình",
                    "is_available": True
                }
            }
        },
        400: {'description': 'Dữ liệu không hợp lệ'}
    }
})
def create_book():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
    
    book = Book(
        title=data['title'],
        author=data.get('author', ''),
        category=data.get('category', '')
    )
    
    try:
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
