"""
Base validator with common validation utilities

Provides shared validation methods and patterns.
"""

from exceptions import ValidationError


class BaseValidator:
    """Base validator with common validation methods"""
    
    @staticmethod
    def validate_required_field(data: dict, field: str, field_display_name: str = None):
        """
        Validate that a required field exists and is not empty
        
        Args:
            data: Data dictionary
            field: Field name to check
            field_display_name: Display name for error messages (defaults to field)
        """
        display_name = field_display_name or field
        
        if field not in data or data[field] is None or data[field] == '':
            raise ValidationError(
                message=f"Missing required field: {display_name}",
                field=field
            )
    
    @staticmethod
    def validate_string_length(value: str, field: str, 
                               min_length: int = None, 
                               max_length: int = None):
        """
        Validate string length constraints
        
        Args:
            value: String value to validate
            field: Field name for error messages
            min_length: Minimum length (inclusive)
            max_length: Maximum length (inclusive)
        """
        if value is None:
            return
        
        value_length = len(value.strip())
        
        if min_length is not None and value_length < min_length:
            raise ValidationError(
                f"{field.capitalize()} must be at least {min_length} character(s) long",
                field=field
            )
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(
                f"{field.capitalize()} must be {max_length} characters or less",
                field=field
            )
    
    @staticmethod
    def validate_not_only_digits(value: str, field: str):
        """
        Validate that a string is not only digits
        
        Args:
            value: String value to validate
            field: Field name for error messages
        """
        if value and value.strip().isdigit():
            raise ValidationError(
                f"{field.capitalize()} cannot contain only numbers",
                field=field
            )
    
    @staticmethod
    def validate_not_empty(value: str, field: str):
        """
        Validate that a string is not empty or only whitespace
        
        Args:
            value: String value to validate
            field: Field name for error messages
        """
        if not value or not value.strip():
            raise ValidationError(
                f"{field.capitalize()} cannot be empty",
                field=field
            )
    
    @staticmethod
    def validate_integer_range(value: int, field: str,
                               min_value: int = None,
                               max_value: int = None):
        """
        Validate integer is within specified range
        
        Args:
            value: Integer value to validate
            field: Field name for error messages
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
        """
        if value is None:
            return
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field.capitalize()} must be a valid number",
                field=field
            )
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(
                f"{field.capitalize()} must be at least {min_value}",
                field=field
            )
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(
                f"{field.capitalize()} must be at most {max_value}",
                field=field
            )
    
    @staticmethod
    def validate_list_type(value: list, field: str, item_type: type = None):
        """
        Validate that value is a list with correct item types
        
        Args:
            value: Value to validate
            field: Field name for error messages
            item_type: Expected type for list items (optional)
        """
        if value is None:
            return
        
        if not isinstance(value, list):
            raise ValidationError(
                f"{field} must be a list",
                field=field
            )
        
        if item_type:
            for item in value:
                try:
                    item_type(item)
                except (ValueError, TypeError):
                    raise ValidationError(
                        f"All {field} must be valid {item_type.__name__}s",
                        field=field
                    )
    
    @staticmethod
    def validate_no_duplicates(value: list, field: str):
        """
        Validate that list contains no duplicates
        
        Args:
            value: List to validate
            field: Field name for error messages
        """
        if value and len(value) != len(set(value)):
            raise ValidationError(
                f"Duplicate {field} are not allowed",
                field=field
            )