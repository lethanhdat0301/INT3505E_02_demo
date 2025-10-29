# Pagination Design Documentation

## Overview

This Flask application implements a comprehensive pagination system with two main types:

1. **Offset-based Pagination** (Traditional page-based)
2. **Cursor-based Pagination** (High-performance for large datasets)

## Features

### ✅ Enhanced Pagination System

#### 1. Standardized Response Format
```json
{
  "data": {
    "items": [...],
    "pagination": {
      "current_page": 1,
      "per_page": 10,
      "total_items": 42,
      "total_pages": 5,
      "has_prev": false,
      "has_next": true,
      "prev_page": null,
      "next_page": 2,
      "links": {
        "first": "/api/v1/books?page=1",
        "last": "/api/v1/books?page=5",
        "prev": null,
        "next": "/api/v1/books?page=2",
        "self": "/api/v1/books?page=1"
      }
    }
  },
  "meta": {
    "status": "success",
    "message": "Showing 1-10 of 42 items",
    "filters": ["search: 'python'"]
  }
}
```

#### 2. Parameter Validation
- Page numbers must be >= 1
- Per-page values must be between 1 and max_per_page
- Automatic error responses for invalid parameters

#### 3. Navigation Links
- Self, first, last, next, previous page URLs
- Preserves all query parameters (search, filters, sorting)

#### 4. Performance Optimizations
- Configurable max items per page
- Efficient SQL queries with proper LIMIT/OFFSET
- Cursor pagination for large datasets

## Usage Examples

### 1. Basic Pagination

```bash
# Get first page with 10 items
GET /api/v1/books?page=1&per_page=10

# Get second page with 5 items
GET /api/v1/books?page=2&per_page=5
```

### 2. Pagination with Search and Filters

```bash
# Search books with pagination
GET /api/v1/books?search=python&page=1&per_page=10

# Filter available books with pagination
GET /api/v1/books?available=true&page=1&per_page=15

# Multiple filters
GET /api/v1/books?category=programming&available=true&page=2&per_page=20
```

### 3. Sorting with Pagination

```bash
# Sort by title (ascending)
GET /api/v1/books?sort_by=title&order=asc&page=1&per_page=10

# Sort by author (descending)
GET /api/v1/books?sort_by=author&order=desc&page=1&per_page=10
```

### 4. Cursor Pagination (Advanced)

```bash
# First page
GET /api/v1/demo/books/cursor?limit=10

# Next page using cursor
GET /api/v1/demo/books/cursor?cursor=10&limit=10&direction=next

# Previous page
GET /api/v1/demo/books/cursor?cursor=5&limit=10&direction=prev
```

## Available Endpoints

### Standard Pagination Endpoints

| Endpoint | Method | Description | Max Per Page |
|----------|--------|-------------|--------------|
| `/api/v1/books` | GET | List books with pagination | 50 |
| `/api/v1/users` | GET | List users with pagination | 50 |
| `/api/v1/borrows` | GET | List borrow records with pagination | 50 |

### Demo Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/demo/books/cursor` | GET | Cursor pagination demo |
| `/api/v1/demo/pagination/info` | GET | Pagination documentation |
| `/api/v1/demo/pagination/test` | GET | Test pagination with sample data |

## Common Parameters

### Offset-based Pagination

| Parameter | Type | Default | Description | Max Value |
|-----------|------|---------|-------------|-----------|
| `page` | integer | 1 | Page number (1-based) | No limit |
| `per_page` | integer | 10 | Items per page | 50-100 (configurable) |
| `sort_by` | string | varies | Field to sort by | Valid model fields |
| `order` | string | 'asc' | Sort direction | 'asc' or 'desc' |
| `search` | string | - | Search term | - |

### Cursor-based Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cursor` | string | - | Cursor position | - |
| `limit` | integer | 10 | Items to return | 100 |
| `direction` | string | 'next' | Direction ('next' or 'prev') | - |

## Error Handling

### Validation Errors (400)

```json
{
  "meta": {
    "status": "error",
    "message": "Invalid pagination parameters"
  },
  "errors": [
    "Page number must be greater than 0",
    "Items per page cannot exceed 50"
  ]
}
```

### Server Errors (500)

```json
{
  "meta": {
    "status": "error",
    "message": "Internal server error occurred"
  },
  "error": "Database connection failed"
}
```

## Implementation Details

### PaginationHelper Class

```python
from utils.pagination import PaginationHelper

# Create from request parameters
pagination = PaginationHelper.from_request(
    max_per_page=50,
    endpoint='books.get_books'
)

# Validate parameters
error = pagination.validate_page_params()
if error:
    return handle_pagination_error(error)

# Apply to query and get formatted response
result = pagination.paginate_query(query)
return jsonify(result), 200
```

### CursorPagination Class

```python
from utils.pagination import CursorPagination

# Create cursor pagination
cursor_pagination = CursorPagination.from_request('id')

# Apply to query
query = cursor_pagination.apply_to_query(query, Model)
items = query.all()

# Format response
result = cursor_pagination.format_response(items, Model)
return jsonify(result), 200
```

## Performance Considerations

### When to Use Each Type

**Offset-based Pagination:**
- ✅ Small to medium datasets (< 10,000 records)
- ✅ User needs to jump to specific pages
- ✅ Need to show total page count
- ❌ Large datasets (performance degrades)
- ❌ Real-time data (inconsistent results)

**Cursor-based Pagination:**
- ✅ Large datasets (> 10,000 records)
- ✅ Real-time feeds
- ✅ API integrations
- ✅ Consistent performance
- ❌ Cannot jump to arbitrary pages
- ❌ More complex for users

### Database Optimization

1. **Add indexes** on commonly sorted fields:
   ```sql
   CREATE INDEX idx_books_title ON books(title);
   CREATE INDEX idx_books_created_at ON books(created_at);
   ```

2. **Use LIMIT efficiently** - avoid large OFFSET values

3. **Consider composite indexes** for multi-field sorting

## Testing the Pagination

### 1. Create Sample Data

```bash
# Run the sample data script
cd Week5
python create_sample_data.py
```

### 2. Test Basic Pagination

```bash
# Test with curl
curl "http://localhost:5000/api/v1/books?page=1&per_page=5"
curl "http://localhost:5000/api/v1/users?page=2&per_page=3"
```

### 3. Test Error Handling

```bash
# Invalid page number
curl "http://localhost:5000/api/v1/books?page=0&per_page=10"

# Invalid per_page
curl "http://localhost:5000/api/v1/books?page=1&per_page=200"
```

### 4. Test Search with Pagination

```bash
# Search with pagination
curl "http://localhost:5000/api/v1/books?search=python&page=1&per_page=5"
```

### 5. Test Demo Endpoints

```bash
# Pagination info
curl "http://localhost:5000/api/v1/demo/pagination/info"

# Test pagination
curl "http://localhost:5000/api/v1/demo/pagination/test?page=2&per_page=5"

# Cursor pagination
curl "http://localhost:5000/api/v1/demo/books/cursor?limit=5"
```

## Next Steps

1. **Add caching** for frequently accessed pages
2. **Implement search highlighting** in results
3. **Add pagination metadata** to HTTP headers
4. **Create client-side pagination helpers** (JavaScript/React)
5. **Add GraphQL support** for flexible pagination
6. **Implement infinite scroll** pagination for web UI

## Troubleshooting

### Common Issues

1. **204 No Content Response**: Database is empty - run `create_sample_data.py`
2. **400 Bad Request**: Check pagination parameters
3. **Performance Issues**: Use cursor pagination for large datasets
4. **Missing Links**: Ensure endpoint names are correct in PaginationHelper

### Debug Mode

Enable debug logging by setting `app.debug = True` in `app.py`