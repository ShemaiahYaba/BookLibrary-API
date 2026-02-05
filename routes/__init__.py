"""
Routes package - Contains all API blueprints
"""

from .books import books_bp
from .authors import authors_bp
from .categories import categories_bp
from .info import info_bp

__all__ = ['books_bp', 'authors_bp', 'categories_bp', 'info_bp']
