"""
Book routes - Blueprint for all book-related endpoints
"""

from flask import Blueprint, request
from services import BookService
from exceptions import (
    BookNotFoundError,
    AuthorNotFoundError,
    ValidationError,
    DuplicateISBNError,
    DatabaseError
)
from utils import create_success_response, create_error_response

books_bp = Blueprint('books', __name__, url_prefix='/books')


@books_bp.route('', methods=['GET'])
def get_books():
    """
    Get all books with optional filtering, search, and pagination
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    - search: Search in title/author name
    - category: Filter by category name
    - year: Filter by publication year
    - author_id: Filter by author ID
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', type=str)
        category = request.args.get('category', type=str)
        year = request.args.get('year', type=int)
        author_id = request.args.get('author_id', type=int)
        
        result = BookService.get_all_books(
            page=page,
            per_page=per_page,
            search=search,
            category=category,
            year=year,
            author_id=author_id
        )
        
        return create_success_response(data=result)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book by ID"""
    try:
        book = BookService.get_book_by_id(book_id)
        return create_success_response(data=book.to_dict())
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@books_bp.route('', methods=['POST'])
def create_book():
    """
    Create a new book
    
    Required fields:
    - title: Book title
    - isbn: ISBN (10 or 13 digits)
    - year: Publication year
    - author_id: ID of existing author
    
    Optional fields:
    - description: Book description
    - pages: Number of pages
    - category_ids: Array of category IDs
    """
    if not request.is_json:
        return create_error_response("Content-Type must be application/json", 400)
    
    try:
        data = request.get_json()
        book = BookService.create_book(data)
        return create_success_response(
            data=book.to_dict(),
            message="Book created successfully",
            status_code=201
        )
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except AuthorNotFoundError as e:
        return create_error_response(str(e), 404)
    except DuplicateISBNError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    if not request.is_json:
        return create_error_response("Content-Type must be application/json", 400)
    
    try:
        data = request.get_json()
        book = BookService.update_book(book_id, data)
        return create_success_response(
            data=book.to_dict(),
            message="Book updated successfully"
        )
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except AuthorNotFoundError as e:
        return create_error_response(str(e), 404)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DuplicateISBNError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    try:
        book = BookService.delete_book(book_id)
        return create_success_response(
            message=f'Book "{book.title}" deleted successfully'
        )
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except DatabaseError as e:
        return create_error_response(str(e), 500)
