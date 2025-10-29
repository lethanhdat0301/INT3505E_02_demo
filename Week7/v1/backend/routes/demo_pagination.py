"""
Advanced pagination examples and demo routes
"""
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import Book, User, BorrowRecord
from utils.pagination import PaginationHelper, CursorPagination, handle_pagination_error

demo_bp = Blueprint('demo', __name__)


@demo_bp.route('/api/v1/demo/books/cursor', methods=['GET'])
@swag_from({
    'tags': ['Demo - Cursor Pagination'],
    'parameters': [
        {'name': 'limit', 'in': 'query', 'type': 'integer', 'default': 10, 'description': 'Số items trả về (max 100)'},
        {'name': 'cursor', 'in': 'query', 'type': 'string', 'description': 'Cursor cho trang tiếp theo'},
        {'name': 'direction', 'in': 'query', 'type': 'string', 'enum': ['next', 'prev'], 'default': 'next'}
    ],
    'responses': {
        200: {
            'description': 'Cursor pagination demo',
            'examples': {
                'application/json': {
                    "data": {
                        "items": [
                            {"id": 1, "title": "Book 1", "author": "Author 1"}
                        ],
                        "pagination": {
                            "limit": 10,
                            "has_more": True,
                            "next_cursor": "1",
                            "prev_cursor": None,
                            "total_returned": 10
                        }
                    },
                    "meta": {
                        "status": "success",
                        "message": "Retrieved 10 items"
                    }
                }
            }
        }
    }
})
def get_books_cursor():
    """
    Demonstrate cursor-based pagination for better performance on large datasets
    """
    cursor_pagination = CursorPagination.from_request('id')
    
    query = Book.query
    query = cursor_pagination.apply_to_query(query, Book)
    
    items = query.all()
    result = cursor_pagination.format_response(items, Book)
    
    return jsonify(result), 200


@demo_bp.route('/api/v1/demo/pagination/info', methods=['GET'])
@swag_from({
    'tags': ['Demo - Pagination Info'],
    'responses': {
        200: {
            'description': 'Pagination capabilities and examples',
            'examples': {
                'application/json': {
                    "pagination_types": {
                        "offset_based": {
                            "description": "Traditional page-number based pagination",
                            "best_for": "Small to medium datasets, user-browsable content",
                            "parameters": ["page", "per_page"],
                            "example_url": "/api/v1/books?page=2&per_page=10"
                        },
                        "cursor_based": {
                            "description": "Cursor-based pagination for better performance",
                            "best_for": "Large datasets, real-time feeds, API integrations",
                            "parameters": ["cursor", "limit", "direction"],
                            "example_url": "/api/v1/demo/books/cursor?cursor=10&limit=20"
                        }
                    }
                }
            }
        }
    }
})
def pagination_info():
    """
    Provide information about pagination capabilities
    """
    return jsonify({
        "data": {
            "pagination_types": {
                "offset_based": {
                    "description": "Traditional page-number based pagination",
                    "best_for": "Small to medium datasets, user-browsable content",
                    "pros": [
                        "Easy to understand",
                        "Users can jump to specific pages",
                        "Shows total page count"
                    ],
                    "cons": [
                        "Performance degrades with large datasets",
                        "Inconsistent results if data changes during browsing"
                    ],
                    "parameters": {
                        "page": "Page number (starts from 1)",
                        "per_page": "Items per page (max 100)"
                    },
                    "example_urls": [
                        "/api/v1/books?page=1&per_page=10",
                        "/api/v1/users?page=2&per_page=5&search=john"
                    ]
                },
                "cursor_based": {
                    "description": "Cursor-based pagination for better performance",
                    "best_for": "Large datasets, real-time feeds, API integrations",
                    "pros": [
                        "Consistent performance on large datasets",
                        "Real-time safe (no duplicates)",
                        "Efficient for forward/backward navigation"
                    ],
                    "cons": [
                        "Cannot jump to arbitrary pages",
                        "More complex to implement and understand"
                    ],
                    "parameters": {
                        "cursor": "Cursor value for pagination position",
                        "limit": "Number of items to return (max 100)",
                        "direction": "Direction to paginate (next/prev)"
                    },
                    "example_urls": [
                        "/api/v1/demo/books/cursor?limit=10",
                        "/api/v1/demo/books/cursor?cursor=15&limit=20&direction=next"
                    ]
                }
            },
            "common_parameters": {
                "search": "Search term for filtering results",
                "sort_by": "Field to sort by",
                "order": "Sort order (asc/desc)"
            },
            "response_format": {
                "structure": {
                    "data": {
                        "items": "Array of result items",
                        "pagination": "Pagination metadata"
                    },
                    "meta": {
                        "status": "Response status",
                        "message": "Human readable message"
                    }
                }
            }
        },
        "meta": {
            "status": "success",
            "message": "Pagination information retrieved"
        }
    }), 200


@demo_bp.route('/api/v1/demo/pagination/test', methods=['GET'])
@swag_from({
    'tags': ['Demo - Pagination Test'],
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 5},
        {'name': 'include_links', 'in': 'query', 'type': 'boolean', 'default': True}
    ],
    'responses': {
        200: {'description': 'Test pagination with sample data'}
    }
})
def test_pagination():
    """
    Test pagination with current data
    """
    include_links = request.args.get('include_links', 'true').lower() == 'true'
    
    pagination_helper = PaginationHelper.from_request(
        max_per_page=20,
        endpoint='demo.test_pagination' if include_links else None
    )
    
    validation_error = pagination_helper.validate_page_params()
    if validation_error:
        return handle_pagination_error(validation_error)
    
    # Get counts for all entities
    book_count = Book.query.count()
    user_count = User.query.count()
    borrow_count = BorrowRecord.query.count()
    
    # Create sample data for testing
    sample_items = []
    for i in range(1, 51):  # 50 sample items
        sample_items.append({
            "id": i,
            "name": f"Sample Item {i}",
            "description": f"This is sample item number {i} for testing pagination"
        })
    
    # Manual pagination simulation
    start_idx = (pagination_helper.page - 1) * pagination_helper.per_page
    end_idx = start_idx + pagination_helper.per_page
    paginated_items = sample_items[start_idx:end_idx]
    
    # Calculate pagination metadata
    total_items = len(sample_items)
    total_pages = (total_items + pagination_helper.per_page - 1) // pagination_helper.per_page
    has_prev = pagination_helper.page > 1
    has_next = pagination_helper.page < total_pages
    
    result = {
        "data": {
            "items": paginated_items,
            "pagination": {
                "current_page": pagination_helper.page,
                "per_page": pagination_helper.per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_prev": has_prev,
                "has_next": has_next,
                "prev_page": pagination_helper.page - 1 if has_prev else None,
                "next_page": pagination_helper.page + 1 if has_next else None
            },
            "database_stats": {
                "books": book_count,
                "users": user_count,
                "borrow_records": borrow_count
            }
        },
        "meta": {
            "status": "success",
            "message": f"Showing {len(paginated_items)} of {total_items} test items"
        }
    }
    
    return jsonify(result), 200