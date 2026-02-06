"""
Base service class with common functionality

Provides shared utilities and patterns for all services.
"""

from typing import Dict
from sqlalchemy.exc import SQLAlchemyError
from database import db
from exceptions import DatabaseError


class BaseService:
    """Base service with common database operations"""
    
    @staticmethod
    def commit_or_rollback(error_message: str = "Database operation failed"):
        """
        Context manager for database transactions
        
        Usage:
            with BaseService.commit_or_rollback("Failed to create record"):
                db.session.add(record)
                db.session.commit()
        """
        class TransactionContext:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    db.session.rollback()
                    if isinstance(exc_val, SQLAlchemyError):
                        raise DatabaseError(f"{error_message}: {str(exc_val)}")
                    return False
                return True
        
        return TransactionContext()
    
    @staticmethod
    def safe_delete(entity, error_message: str = "Failed to delete"):
        """
        Safely delete an entity with rollback on error
        
        Args:
            entity: Database entity to delete
            error_message: Custom error message
            
        Returns:
            The deleted entity
        """
        try:
            db.session.delete(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"{error_message}: {str(e)}")
    
    @staticmethod
    def safe_commit(error_message: str = "Failed to commit changes"):
        """
        Safely commit changes with rollback on error
        
        Args:
            error_message: Custom error message
        """
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"{error_message}: {str(e)}")
    
    @staticmethod
    def build_pagination_response(paginated, page: int, per_page: int, 
                                   item_key: str = 'items') -> Dict:
        """
        Build standardized pagination response
        
        Args:
            paginated: SQLAlchemy pagination object
            page: Current page number
            per_page: Items per page
            item_key: Key name for items in response
            
        Returns:
            Dictionary with pagination metadata
        """
        return {
            item_key: paginated.items,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }