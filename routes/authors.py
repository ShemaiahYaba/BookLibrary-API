"""
Author routes - Blueprint for all author-related endpoints
"""

from flask import Blueprint, request
from service import AuthorService
from exceptions import (
    AuthorNotFoundError,
    ValidationError,
    DatabaseError
)
from utils import create_success_response, create_error_response

authors_bp = Blueprint('authors', __name__, url_prefix='/authors')


@authors_bp.route('', methods=['GET'])
def get_authors():
    """
    Get all authors with pagination
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = AuthorService.get_all_authors(page=page, per_page=per_page)
        return create_success_response(data=result)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@authors_bp.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get a specific author by ID with their books"""
    try:
        include_books = request.args.get('include_books', 'true').lower() == 'true'
        author = AuthorService.get_author_by_id(author_id, include_books)
        return create_success_response(data=author.to_dict(include_books=include_books))
    except AuthorNotFoundError as e:
        return create_error_response(str(e), 404)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@authors_bp.route('', methods=['POST'])
def create_author():
    """
    Create a new author
    
    Required fields:
    - name: Author name
    
    Optional fields:
    - bio: Author biography
    - country: Author's country
    """
    if not request.is_json:
        return create_error_response("Content-Type must be application/json", 400)
    
    try:
        data = request.get_json()
        author = AuthorService.create_author(data)
        return create_success_response(
            data=author.to_dict(),
            message="Author created successfully",
            status_code=201
        )
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@authors_bp.route('/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Update an existing author"""
    if not request.is_json:
        return create_error_response("Content-Type must be application/json", 400)
    
    try:
        data = request.get_json()
        author = AuthorService.update_author(author_id, data)
        return create_success_response(
            data=author.to_dict(),
            message="Author updated successfully"
        )
    except AuthorNotFoundError as e:
        return create_error_response(str(e), 404)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@authors_bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Delete an author (only if they have no books)"""
    try:
        author = AuthorService.delete_author(author_id)
        return create_success_response(
            message=f'Author "{author.name}" deleted successfully'
        )
    except AuthorNotFoundError as e:
        return create_error_response(str(e), 404)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)
