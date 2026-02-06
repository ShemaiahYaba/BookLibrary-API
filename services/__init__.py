"""
Services package - Contains all business logic services

This modular structure separates concerns and makes the codebase
more maintainable and testable.
"""

from .base_service import BaseService
from .book_service import BookService
from .author_service import AuthorService
from .category_service import CategoryService

__all__ = [
    'BaseService',
    'BookService',
    'AuthorService',
    'CategoryService'
]