"""
Category routes - Blueprint for all category-related endpoints
"""

from flask import Blueprint, request
from service import CategoryService
from exceptions import (
    CategoryNotFoundError,
    ValidationError,
    DuplicateCategoryError,
    DatabaseError
)
from utils import create_success_response, create_error_response

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


@categories_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = CategoryService.get_all_categories()
        return create_success_response(
            data={'categories': [cat.to_dict() for cat in categories]}
        )
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category by ID"""
    try:
        include_books = request.args.get('include_books', 'false').lower() == 'true'
        category = CategoryService.get_category_by_id(category_id)
        return create_success_response(data=category.to_dict(include_books=include_books))
    except CategoryNotFoundError as e:
        return create_error_response(str(e), 404)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@categories_bp.route('', methods=['POST'])
def create_category():
    """
    Create a new category
    
    Required fields:
    - name: Category name (unique)
    
    Optional fields:
    - description: Category description
    """
    if not request.is_json:
        return create_error_response("Content-Type must be application/json", 400)
    
    try:
        data = request.get_json()
        category = CategoryService.create_category(data)
        return create_success_response(
            data=category.to_dict(),
            message="Category created successfully",
            status_code=201
        )
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DuplicateCategoryError as e:
        return create_error_response(str(e), 400)
    except DatabaseError as e:
        return create_error_response(str(e), 500)


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        category = CategoryService.delete_category(category_id)
        return create_success_response(
            message=f'Category "{category.name}" deleted successfully'
        )
    except CategoryNotFoundError as e:
        return create_error_response(str(e), 404)
    except DatabaseError as e:
        return create_error_response(str(e), 500)
