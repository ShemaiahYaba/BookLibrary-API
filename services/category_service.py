"""
Category service - Handles all category-related business logic

Provides CRUD operations for categories with proper validation
and error handling.
"""

from typing import List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import Category
from validators import CategoryValidator
from exceptions import (
    CategoryNotFoundError,
    DuplicateCategoryError,
    DatabaseError
)
from .base_service import BaseService


class CategoryService(BaseService):
    """Service for category operations"""
    
    @staticmethod
    def get_all_categories() -> List[Category]:
        """
        Get all categories
        
        Returns:
            List of all categories, ordered by name
        """
        try:
            return Category.query.order_by(Category.name).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch categories: {str(e)}")
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Category:
        """
        Get a specific category by ID
        
        Args:
            category_id: Category ID
            
        Returns:
            Category object
            
        Raises:
            CategoryNotFoundError: If category doesn't exist
        """
        category = db.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        return category
    
    @staticmethod
    def create_category(data: dict) -> Category:
        """
        Create a new category
        
        Args:
            data: Category data dictionary
            
        Returns:
            Created category object
            
        Raises:
            ValidationError: If data is invalid
            DuplicateCategoryError: If category name already exists
        """
        # Validate data
        CategoryValidator.validate_category_data(data)
        
        # Check for duplicate name
        CategoryService._check_duplicate_name(data['name'])
        
        try:
            # Create category object
            category = CategoryService._create_category_object(data)
            
            db.session.add(category)
            db.session.commit()
            
            return category
            
        except IntegrityError:
            db.session.rollback()
            raise DuplicateCategoryError(data['name'])
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create category: {str(e)}")
    
    @staticmethod
    def _create_category_object(data: dict) -> Category:
        """Create category object from data"""
        return Category(
            name=data['name'].strip(),
            description=data.get('description', '').strip() if data.get('description') else None
        )
    
    @staticmethod
    def _check_duplicate_name(name: str):
        """Check if category name already exists"""
        existing = Category.query.filter_by(name=name.strip()).first()
        if existing:
            raise DuplicateCategoryError(name)
    
    @staticmethod
    def delete_category(category_id: int) -> Category:
        """
        Delete a category
        
        Args:
            category_id: Category ID
            
        Returns:
            Deleted category object
        """
        category = CategoryService.get_category_by_id(category_id)
        return CategoryService.safe_delete(category, "Failed to delete category")