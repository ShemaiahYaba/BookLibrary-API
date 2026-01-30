"""
Validation logic for book data

Separating validation into its own module:
- Makes validation logic reusable
- Easier to test
- Clear single responsibility
"""

from datetime import datetime
from exceptions import ValidationError


class BookValidator:
    """Validates book data according to business rules"""
    
    @staticmethod
    def validate_required_fields(data: dict, is_update: bool = False) -> None:
        """
        Validate that required fields are present
        
        Raises:
            ValidationError: If required fields are missing
        """
        if is_update:
            # For updates, no fields are strictly required
            return
        
        required_fields = ['title', 'author', 'isbn', 'year']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(
                    message=f"Missing required field: {field}",
                    field=field
                )
    
    @staticmethod
    def validate_year(year: int) -> None:
        """
        Validate that year is reasonable
        
        Args:
            year: Publication year to validate
            
        Raises:
            ValidationError: If year is invalid
        """
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            raise ValidationError(
                message="Year must be a valid number",
                field="year"
            )
        
        current_year = datetime.now().year
        if year_int < 1000 or year_int > current_year:
            raise ValidationError(
                message=f"Year must be between 1000 and {current_year}",
                field="year"
            )
    
    @staticmethod
    def validate_isbn(isbn: str) -> None:
        """
        Validate ISBN format
        
        Args:
            isbn: ISBN to validate
            
        Raises:
            ValidationError: If ISBN format is invalid
        """
        # Remove common separators
        clean_isbn = str(isbn).replace('-', '').replace(' ', '')
        
        if not clean_isbn.isdigit():
            raise ValidationError(
                message="ISBN must contain only digits (hyphens and spaces allowed)",
                field="isbn"
            )
        
        if len(clean_isbn) not in (10, 13):
            raise ValidationError(
                message="ISBN must be 10 or 13 digits",
                field="isbn"
            )
    
    @classmethod
    def validate_book_data(cls, data: dict, is_update: bool = False) -> None:
        """
        Validate all book data
        
        Args:
            data: Dictionary containing book data
            is_update: Whether this is an update operation
            
        Raises:
            ValidationError: If any validation fails
        """
        cls.validate_required_fields(data, is_update)
        
        if 'year' in data:
            cls.validate_year(data['year'])
        
        if 'isbn' in data:
            cls.validate_isbn(data['isbn'])
        
        # Additional validations can be added here
        if 'title' in data and len(data['title'].strip()) == 0:
            raise ValidationError(
                message="Title cannot be empty",
                field="title"
            )
        
        if 'author' in data and len(data['author'].strip()) == 0:
            raise ValidationError(
                message="Author cannot be empty",
                field="author"
            )
