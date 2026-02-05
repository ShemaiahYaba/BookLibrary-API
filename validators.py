"""
Validation logic for all models

Centralized validation ensures data integrity before database operations.
"""

from datetime import datetime
from exceptions import ValidationError


class BookValidator:
    """Validates book data"""
    
    @staticmethod
    def validate_required_fields(data: dict, is_update: bool = False) -> None:
        """Validate required fields for book"""
        if is_update:
            return  # For updates, no fields are strictly required
        
        required_fields = ['title', 'isbn', 'year', 'author_id']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                raise ValidationError(
                    message=f"Missing required field: {field}",
                    field=field
                )
    
    @staticmethod
    def validate_year(year: int) -> None:
        """Validate publication year"""
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            raise ValidationError("Year must be a valid number", field="year")
        
        current_year = datetime.now().year
        if year_int < 1000 or year_int > current_year:
            raise ValidationError(
                f"Year must be between 1000 and {current_year}",
                field="year"
            )
    
    @staticmethod
    def validate_isbn(isbn: str) -> None:
        """Validate ISBN format"""
        clean_isbn = str(isbn).replace('-', '').replace(' ', '')
        
        if not clean_isbn.isdigit():
            raise ValidationError(
                "ISBN must contain only digits",
                field="isbn"
            )
        
        if len(clean_isbn) not in (10, 13):
            raise ValidationError(
                "ISBN must be 10 or 13 digits",
                field="isbn"
            )
    
    @staticmethod
    def validate_pages(pages: int) -> None:
        """Validate page count"""
        if pages is not None:
            try:
                pages_int = int(pages)
                if pages_int < 1:
                    raise ValidationError("Pages must be positive", field="pages")
            except (ValueError, TypeError):
                raise ValidationError("Pages must be a number", field="pages")
    
    @classmethod
    def validate_book_data(cls, data: dict, is_update: bool = False) -> None:
        """Validate all book data"""
        cls.validate_required_fields(data, is_update)
        
        if 'year' in data:
            cls.validate_year(data['year'])
        
        if 'isbn' in data:
            cls.validate_isbn(data['isbn'])
        
        if 'pages' in data:
            cls.validate_pages(data['pages'])
        
        if 'title' in data and not data['title'].strip():
            raise ValidationError("Title cannot be empty", field="title")


class AuthorValidator:
    """Validates author data"""
    
    @staticmethod
    def validate_required_fields(data: dict, is_update: bool = False) -> None:
        """Validate required fields for author"""
        if is_update:
            return
        
        if 'name' not in data or not data['name']:
            raise ValidationError("Missing required field: name", field="name")
    
    @staticmethod
    def validate_name(name: str) -> None:
        """Validate author name"""
        if not name or not name.strip():
            raise ValidationError("Author name cannot be empty", field="name")
        
        if len(name) > 200:
            raise ValidationError("Author name too long (max 200 characters)", field="name")
    
    @classmethod
    def validate_author_data(cls, data: dict, is_update: bool = False) -> None:
        """Validate all author data"""
        cls.validate_required_fields(data, is_update)
        
        if 'name' in data:
            cls.validate_name(data['name'])


class CategoryValidator:
    """Validates category data"""
    
    @staticmethod
    def validate_required_fields(data: dict, is_update: bool = False) -> None:
        """Validate required fields for category"""
        if is_update:
            return
        
        if 'name' not in data or not data['name']:
            raise ValidationError("Missing required field: name", field="name")
    
    @staticmethod
    def validate_name(name: str) -> None:
        """Validate category name"""
        if not name or not name.strip():
            raise ValidationError("Category name cannot be empty", field="name")
        
        if len(name) > 100:
            raise ValidationError("Category name too long (max 100 characters)", field="name")
    
    @classmethod
    def validate_category_data(cls, data: dict, is_update: bool = False) -> None:
        """Validate all category data"""
        cls.validate_required_fields(data, is_update)
        
        if 'name' in data:
            cls.validate_name(data['name'])


class PaginationValidator:
    """Validates pagination parameters"""
    
    @staticmethod
    def validate_pagination(page: int = None, per_page: int = None) -> tuple:
        """
        Validate and return pagination parameters
        
        Returns:
            Tuple of (page, per_page)
        """
        # Default values
        page = page if page is not None else 1
        per_page = per_page if per_page is not None else 10
        
        # Validate page
        try:
            page = int(page)
            if page < 1:
                raise ValidationError("Page must be >= 1", field="page")
        except (ValueError, TypeError):
            raise ValidationError("Page must be a number", field="page")
        
        # Validate per_page
        try:
            per_page = int(per_page)
            if per_page < 1:
                raise ValidationError("Per page must be >= 1", field="per_page")
            if per_page > 100:
                raise ValidationError("Per page must be <= 100", field="per_page")
        except (ValueError, TypeError):
            raise ValidationError("Per page must be a number", field="per_page")
        
        return page, per_page
