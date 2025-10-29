"""
Pagination utilities for Flask SQLAlchemy applications
"""
from flask import request, url_for
from typing import Dict, Any, Optional, List
from math import ceil


class PaginationHelper:
    """
    A comprehensive pagination helper class that provides
    standardized pagination functionality across all endpoints
    """
    
    def __init__(self, 
                 page: int = 1, 
                 per_page: int = 10, 
                 max_per_page: int = 100,
                 endpoint: Optional[str] = None):
        """
        Initialize pagination helper
        
        Args:
            page: Current page number (1-based)
            per_page: Number of items per page
            max_per_page: Maximum allowed items per page
            endpoint: Flask endpoint name for generating links
        """
        self.page = max(1, page)  # Ensure page is at least 1
        self.per_page = min(max(1, per_page), max_per_page)  # Clamp per_page
        self.max_per_page = max_per_page
        self.endpoint = endpoint
        
    @classmethod
    def from_request(cls, 
                     max_per_page: int = 100,
                     endpoint: Optional[str] = None) -> 'PaginationHelper':
        """
        Create PaginationHelper from Flask request args
        
        Args:
            max_per_page: Maximum allowed items per page
            endpoint: Flask endpoint name for generating links
            
        Returns:
            PaginationHelper instance
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        return cls(page=page, per_page=per_page, 
                  max_per_page=max_per_page, endpoint=endpoint)
    
    def paginate_query(self, query) -> Dict[str, Any]:
        """
        Apply pagination to a SQLAlchemy query and return formatted result
        
        Args:
            query: SQLAlchemy query object
            
        Returns:
            Dictionary containing pagination data and items
        """
        # Execute pagination
        pagination = query.paginate(
            page=self.page, 
            per_page=self.per_page, 
            error_out=False
        )
        
        # Convert items to dictionaries if they have to_dict method
        items = []
        for item in pagination.items:
            if hasattr(item, 'to_dict'):
                items.append(item.to_dict())
            else:
                items.append(item)
        
        # Build response
        result = {
            "data": {
                "items": items,
                "pagination": {
                    "current_page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_items": pagination.total,
                    "total_pages": pagination.pages,
                    "has_prev": pagination.has_prev,
                    "has_next": pagination.has_next,
                    "prev_page": pagination.prev_num if pagination.has_prev else None,
                    "next_page": pagination.next_num if pagination.has_next else None
                }
            },
            "meta": {
                "status": "success",
                "message": self._get_status_message(pagination)
            }
        }
        
        # Add navigation links if endpoint is provided
        if self.endpoint:
            result["data"]["pagination"]["links"] = self._generate_links(pagination)
            
        return result
    
    def _get_status_message(self, pagination) -> str:
        """Generate appropriate status message based on pagination results"""
        if pagination.total == 0:
            return "No data found"
        
        start_item = (pagination.page - 1) * pagination.per_page + 1
        end_item = min(pagination.page * pagination.per_page, pagination.total)
        
        return f"Showing {start_item}-{end_item} of {pagination.total} items"
    
    def _generate_links(self, pagination) -> Dict[str, Optional[str]]:
        """Generate navigation links for pagination"""
        def make_url(page_num):
            args = dict(request.args)
            args['page'] = page_num
            return url_for(self.endpoint, **args)
        
        links = {
            "first": make_url(1),
            "last": make_url(pagination.pages) if pagination.pages > 0 else None,
            "prev": make_url(pagination.prev_num) if pagination.has_prev else None,
            "next": make_url(pagination.next_num) if pagination.has_next else None,
            "self": make_url(pagination.page)
        }
        
        return links
    
    def validate_page_params(self) -> Optional[Dict[str, Any]]:
        """
        Validate pagination parameters
        
        Returns:
            Error dict if validation fails, None if valid
        """
        errors = []
        
        if self.page < 1:
            errors.append("Page number must be greater than 0")
            
        if self.per_page < 1:
            errors.append("Items per page must be greater than 0")
            
        if self.per_page > self.max_per_page:
            errors.append(f"Items per page cannot exceed {self.max_per_page}")
        
        if errors:
            return {
                "meta": {
                    "status": "error",
                    "message": "Invalid pagination parameters"
                },
                "errors": errors
            }
        
        return None


class CursorPagination:
    """
    Cursor-based pagination for better performance on large datasets
    Uses a cursor (typically timestamp or ID) instead of page numbers
    """
    
    def __init__(self, 
                 cursor_field: str,
                 limit: int = 10,
                 cursor: Optional[str] = None,
                 direction: str = 'next'):
        """
        Initialize cursor pagination
        
        Args:
            cursor_field: Database field to use as cursor (e.g., 'id', 'created_at')
            limit: Number of items to return
            cursor: Current cursor position
            direction: 'next' or 'prev'
        """
        self.cursor_field = cursor_field
        self.limit = min(max(1, limit), 100)  # Clamp limit between 1-100
        self.cursor = cursor
        self.direction = direction
    
    @classmethod
    def from_request(cls, cursor_field: str) -> 'CursorPagination':
        """Create CursorPagination from Flask request args"""
        limit = request.args.get('limit', 10, type=int)
        cursor = request.args.get('cursor', type=str)
        direction = request.args.get('direction', 'next', type=str)
        
        return cls(cursor_field=cursor_field, limit=limit, 
                  cursor=cursor, direction=direction)
    
    def apply_to_query(self, query, model_class):
        """
        Apply cursor pagination to query
        
        Args:
            query: SQLAlchemy query
            model_class: SQLAlchemy model class
            
        Returns:
            Modified query with cursor pagination applied
        """
        cursor_column = getattr(model_class, self.cursor_field)
        
        if self.cursor:
            if self.direction == 'next':
                query = query.filter(cursor_column > self.cursor)
                query = query.order_by(cursor_column.asc())
            else:  # prev
                query = query.filter(cursor_column < self.cursor)
                query = query.order_by(cursor_column.desc())
        else:
            query = query.order_by(cursor_column.asc())
        
        return query.limit(self.limit + 1)  # +1 to check if there's a next page
    
    def format_response(self, items: List, model_class) -> Dict[str, Any]:
        """
        Format cursor pagination response
        
        Args:
            items: List of query results
            model_class: SQLAlchemy model class
            
        Returns:
            Formatted response dictionary
        """
        has_more = len(items) > self.limit
        if has_more:
            items = items[:-1]  # Remove the extra item
        
        # Convert items to dictionaries
        formatted_items = []
        for item in items:
            if hasattr(item, 'to_dict'):
                formatted_items.append(item.to_dict())
            else:
                formatted_items.append(item)
        
        # Get cursors for navigation
        next_cursor = None
        prev_cursor = None
        
        if formatted_items:
            cursor_field_value = getattr(items[-1], self.cursor_field)
            next_cursor = str(cursor_field_value) if has_more else None
            
            cursor_field_value = getattr(items[0], self.cursor_field)
            prev_cursor = str(cursor_field_value) if self.cursor else None
        
        return {
            "data": {
                "items": formatted_items,
                "pagination": {
                    "limit": self.limit,
                    "has_more": has_more,
                    "next_cursor": next_cursor,
                    "prev_cursor": prev_cursor,
                    "total_returned": len(formatted_items)
                }
            },
            "meta": {
                "status": "success",
                "message": f"Retrieved {len(formatted_items)} items"
            }
        }


def handle_pagination_error(error_dict: Dict[str, Any]) -> tuple:
    """
    Handle pagination validation errors
    
    Args:
        error_dict: Error dictionary from validation
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    return error_dict, 400