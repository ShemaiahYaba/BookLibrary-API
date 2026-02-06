"""
Author validator - Validates all author-related data

Ensures data integrity for author operations.
"""

from exceptions import ValidationError
from .base_validator import BaseValidator


class AuthorValidator(BaseValidator):
    """Validates author data"""
    
    # Constants for validation
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 200
    MAX_BIO_LENGTH = 2000
    MAX_COUNTRY_LENGTH = 100
    
    @classmethod
    def validate_author_data(cls, data: dict, is_update: bool = False) -> None:
        """
        Validate all author data
        
        Args:
            data: Author data dictionary
            is_update: Whether this is an update operation
        """
        # Validate required fields (only for create)
        if not is_update:
            cls.validate_required_fields(data)
        
        # Validate individual fields if present
        if 'name' in data:
            cls.validate_name(data['name'])
        
        if 'bio' in data:
            cls.validate_bio(data['bio'])
        
        if 'country' in data:
            cls.validate_country(data['country'])
    
    @classmethod
    def validate_required_fields(cls, data: dict) -> None:
        """Validate required fields for author creation"""
        cls.validate_required_field(data, 'name', 'author name')
    
    @classmethod
    def validate_name(cls, name: str) -> None:
        """Validate author name"""
        cls.validate_not_empty(name, 'author name')
        cls.validate_string_length(name, 'author name',
                                   min_length=cls.MIN_NAME_LENGTH,
                                   max_length=cls.MAX_NAME_LENGTH)
        cls.validate_not_only_digits(name, 'author name')
    
    @classmethod
    def validate_bio(cls, bio: str) -> None:
        """Validate author biography"""
        if bio is not None:
            cls.validate_string_length(bio, 'biography',
                                       max_length=cls.MAX_BIO_LENGTH)
    
    @classmethod
    def validate_country(cls, country: str) -> None:
        """Validate author country"""
        if country is not None:
            cls.validate_string_length(country, 'country name',
                                       max_length=cls.MAX_COUNTRY_LENGTH)
            cls.validate_not_only_digits(country, 'country name')