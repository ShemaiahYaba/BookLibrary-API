"""
Book validator - Validates all book-related data

Ensures data integrity for book operations.
"""

from datetime import datetime
from exceptions import ValidationError
from .base_validator import BaseValidator


class BookValidator(BaseValidator):
    """Validates book data"""
    
    # Constants for validation
    MIN_YEAR = 1000
    MIN_PAGES = 1
    MAX_PAGES = 50000
    MAX_TITLE_LENGTH = 300
    MAX_DESCRIPTION_LENGTH = 5000
    MIN_ISBN_LENGTH = 10
    MAX_ISBN_LENGTH = 13
    MAX_CATEGORIES = 10
    
    @classmethod
    def validate_book_data(cls, data: dict, is_update: bool = False) -> None:
        """
        Validate all book data
        
        Args:
            data: Book data dictionary
            is_update: Whether this is an update operation
        """
        # Validate required fields (only for create)
        if not is_update:
            cls.validate_required_fields(data)
        
        # Validate individual fields if present
        if 'title' in data:
            cls.validate_title(data['title'])
        
        if 'isbn' in data:
            cls.validate_isbn(data['isbn'])
        
        if 'year' in data:
            cls.validate_year(data['year'])
        
        if 'pages' in data:
            cls.validate_pages(data['pages'])
        
        if 'description' in data:
            cls.validate_description(data['description'])
        
        if 'category_ids' in data:
            cls.validate_category_ids(data['category_ids'])
    
    @classmethod
    def validate_required_fields(cls, data: dict) -> None:
        """Validate required fields for book creation"""
        required_fields = ['title', 'isbn', 'year', 'author_id']
        
        for field in required_fields:
            cls.validate_required_field(data, field)
    
    @classmethod
    def validate_title(cls, title: str) -> None:
        """Validate book title"""
        cls.validate_not_empty(title, 'title')
        cls.validate_string_length(title, 'title', 
                                   min_length=1, 
                                   max_length=cls.MAX_TITLE_LENGTH)
    
    @classmethod
    def validate_isbn(cls, isbn: str) -> None:
        """Validate ISBN format"""
        # Clean ISBN (remove hyphens and spaces)
        clean_isbn = str(isbn).replace('-', '').replace(' ', '')
        
        # Check if digits only
        if not clean_isbn.isdigit():
            raise ValidationError(
                "ISBN must contain only digits (hyphens and spaces are allowed)",
                field="isbn"
            )
        
        # Check length
        if len(clean_isbn) not in (cls.MIN_ISBN_LENGTH, cls.MAX_ISBN_LENGTH):
            raise ValidationError(
                f"ISBN must be {cls.MIN_ISBN_LENGTH} or {cls.MAX_ISBN_LENGTH} digits",
                field="isbn"
            )
    
    @classmethod
    def validate_year(cls, year: int) -> None:
        """Validate publication year"""
        current_year = datetime.now().year
        cls.validate_integer_range(year, 'year', 
                                   min_value=cls.MIN_YEAR, 
                                   max_value=current_year)
    
    @classmethod
    def validate_pages(cls, pages: int) -> None:
        """Validate page count"""
        if pages is not None:
            cls.validate_integer_range(pages, 'pages',
                                       min_value=cls.MIN_PAGES,
                                       max_value=cls.MAX_PAGES)
    
    @classmethod
    def validate_description(cls, description: str) -> None:
        """Validate book description"""
        if description is not None:
            cls.validate_string_length(description, 'description',
                                       max_length=cls.MAX_DESCRIPTION_LENGTH)
    
    @classmethod
    def validate_category_ids(cls, category_ids: list) -> None:
        """Validate category IDs"""
        if category_ids is None:
            return
        
        # Must be a list
        cls.validate_list_type(category_ids, 'category_ids', int)
        
        # No duplicates allowed
        cls.validate_no_duplicates(category_ids, 'category IDs')
        
        # Limit number of categories
        if len(category_ids) > cls.MAX_CATEGORIES:
            raise ValidationError(
                f"A book can have a maximum of {cls.MAX_CATEGORIES} categories",
                field="category_ids"
            )