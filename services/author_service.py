"""
Author service - Handles all author-related business logic

Provides CRUD operations for authors with proper validation
and error handling.
"""

from typing import Dict
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models import Author
from validators import AuthorValidator, PaginationValidator
from exceptions import (
    AuthorNotFoundError,
    DatabaseError,
    ValidationError
)
from .base_service import BaseService


class AuthorService(BaseService):
    """Service for author operations"""
    
    @staticmethod
    def get_all_authors(page: int = 1, per_page: int = 10) -> Dict:
        """
        Get all authors with pagination
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Dictionary with authors and pagination info
        """
        # Validate pagination
        page, per_page = PaginationValidator.validate_pagination(page, per_page)
        
        try:
            paginated = Author.query.order_by(Author.name).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'authors': [author.to_dict() for author in paginated.items],
                'total': paginated.total,
                'page': page,
                'per_page': per_page,
                'pages': paginated.pages
            }
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch authors: {str(e)}")
    
    @staticmethod
    def get_author_by_id(author_id: int, include_books: bool = False) -> Author:
        """
        Get a specific author by ID
        
        Args:
            author_id: Author ID
            include_books: Whether to load books (for display purposes)
            
        Returns:
            Author object
            
        Raises:
            AuthorNotFoundError: If author doesn't exist
        """
        author = db.session.get(Author, author_id)
        if not author:
            raise AuthorNotFoundError(author_id)
        return author
    
    @staticmethod
    def create_author(data: dict) -> Author:
        """
        Create a new author
        
        Args:
            data: Author data dictionary
            
        Returns:
            Created author object
            
        Raises:
            ValidationError: If data is invalid
        """
        # Validate data
        AuthorValidator.validate_author_data(data)
        
        try:
            # Create author object
            author = AuthorService._create_author_object(data)
            
            db.session.add(author)
            db.session.commit()
            
            return author
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create author: {str(e)}")
    
    @staticmethod
    def _create_author_object(data: dict) -> Author:
        """Create author object from data"""
        return Author(
            name=data['name'].strip(),
            bio=data.get('bio', '').strip() if data.get('bio') else None,
            country=data.get('country', '').strip() if data.get('country') else None
        )
    
    @staticmethod
    def update_author(author_id: int, data: dict) -> Author:
        """
        Update an existing author
        
        Args:
            author_id: Author ID
            data: Updated data
            
        Returns:
            Updated author object
        """
        # Validate data
        AuthorValidator.validate_author_data(data, is_update=True)
        
        # Get the author
        author = AuthorService.get_author_by_id(author_id)
        
        try:
            # Update fields
            AuthorService._update_author_fields(author, data)
            
            db.session.commit()
            return author
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update author: {str(e)}")
    
    @staticmethod
    def _update_author_fields(author: Author, data: dict):
        """Update individual author fields from data"""
        if 'name' in data:
            author.name = data['name'].strip()
        
        if 'bio' in data:
            author.bio = data['bio'].strip() if data['bio'] else None
        
        if 'country' in data:
            author.country = data['country'].strip() if data['country'] else None
    
    @staticmethod
    def delete_author(author_id: int) -> Author:
        """
        Delete an author (only if they have no books)
        
        Args:
            author_id: Author ID
            
        Returns:
            Deleted author object
            
        Raises:
            ValidationError: If author has books
        """
        author = AuthorService.get_author_by_id(author_id)
        
        # Check if author has books
        book_count = author.books.count()
        if book_count > 0:
            raise ValidationError(
                f"Cannot delete author with existing books. "
                f"Delete {book_count} book(s) first."
            )
        
        return AuthorService.safe_delete(author, "Failed to delete author")