"""
Category validator - Validates all category-related data

Ensures data integrity for category operations.
"""

from exceptions import ValidationError
from .base_validator import BaseValidator


class CategoryValidator(BaseValidator):
    """Validates category data"""
    
    # Constants for validation
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    
    @classmethod
    def validate_category_data(cls, data: dict, is_update: bool = False) -> None:
        """
        Validate all category data
        
        Args:
            data: Category data dictionary
            is_update: Whether this is an update operation
        """
        # Validate required fields (only for create)
        if not is_update:
            cls.validate_required_fields(data)
        
        # Validate individual fields if present
        if 'name' in data:
            cls.validate_name(data['name'])
        
        if 'description' in data:
            cls.validate_description(data['description'])
    
    @classmethod
    def validate_required_fields(cls, data: dict) -> None:
        """Validate required fields for category creation"""
        cls.validate_required_field(data, 'name', 'category name')
    
    @classmethod
    def validate_name(cls, name: str) -> None:
        """Validate category name"""
        cls.validate_not_empty(name, 'category name')
        cls.validate_string_length(name, 'category name',
                                   min_length=cls.MIN_NAME_LENGTH,
                                   max_length=cls.MAX_NAME_LENGTH)
        cls.validate_not_only_digits(name, 'category name')
    
    @classmethod
    def validate_description(cls, description: str) -> None:
        """Validate category description"""
        if description is not None:
            cls.validate_string_length(description, 'category description',
                                       max_length=cls.MAX_DESCRIPTION_LENGTH)