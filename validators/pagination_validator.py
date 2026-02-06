"""
Pagination validator - Validates pagination parameters

Ensures valid pagination across all endpoints.
"""

from exceptions import ValidationError
from .base_validator import BaseValidator


class PaginationValidator(BaseValidator):
    """Validates pagination parameters"""
    
    # Constants for validation
    MIN_PAGE = 1
    MIN_PER_PAGE = 1
    MAX_PER_PAGE = 100
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    
    @classmethod
    def validate_pagination(cls, page: int = None, per_page: int = None) -> tuple:
        """
        Validate and return pagination parameters
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (page, per_page) with validated values
        """
        # Apply defaults
        page = page if page is not None else cls.DEFAULT_PAGE
        per_page = per_page if per_page is not None else cls.DEFAULT_PER_PAGE
        
        # Validate page
        cls.validate_integer_range(page, 'page', min_value=cls.MIN_PAGE)
        
        # Validate per_page
        cls.validate_integer_range(per_page, 'per_page',
                                   min_value=cls.MIN_PER_PAGE,
                                   max_value=cls.MAX_PER_PAGE)
        
        return int(page), int(per_page)