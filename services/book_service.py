"""
Book service - Handles all book-related business logic

Demonstrates:
- CRUD operations with database
- Complex queries (search, filter, pagination)
- JOIN operations
- Transaction management
"""

from typing import Dict
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import Book, Author, Category
from validators import BookValidator, PaginationValidator
from exceptions import (
    BookNotFoundError,
    AuthorNotFoundError,
    DuplicateISBNError,
    DatabaseError,
    ValidationError
)
from .base_service import BaseService


class BookService(BaseService):
    """Service for book operations"""
    
    @staticmethod
    def get_all_books(page: int = 1, per_page: int = 10, 
                      search: str = None, category: str = None, 
                      year: int = None, author_id: int = None) -> Dict:
        """
        Get all books with optional filtering, search, and pagination
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            search: Search term for title/author
            category: Filter by category name
            year: Filter by publication year
            author_id: Filter by author ID
            
        Returns:
            Dictionary with books, pagination info
        """
        # Validate pagination
        page, per_page = PaginationValidator.validate_pagination(page, per_page)
        
        # Build query using helper method
        query = BookService._build_book_query(search, category, year, author_id)
        
        # Execute paginated query
        try:
            paginated = query.order_by(Book.created_at.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'books': [book.to_dict() for book in paginated.items],
                'total': paginated.total,
                'page': page,
                'per_page': per_page,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch books: {str(e)}")
    
    @staticmethod
    def _build_book_query(search: str = None, category: str = None,
                          year: int = None, author_id: int = None):
        """
        Build book query with filters
        
        Args:
            search: Search term for title/author
            category: Filter by category name
            year: Filter by publication year
            author_id: Filter by author ID
            
        Returns:
            SQLAlchemy query object
        """
        query = Book.query
        
        # Apply search filter (searches in both title and author name)
        if search:
            search_term = f"%{search}%"
            query = query.join(Author).filter(
                or_(
                    Book.title.ilike(search_term),
                    Author.name.ilike(search_term)
                )
            )
        
        # Apply category filter
        if category:
            query = query.join(Book.categories).filter(
                Category.name.ilike(f"%{category}%")
            )
        
        # Apply year filter
        if year:
            query = query.filter(Book.year == year)
        
        # Apply author filter
        if author_id:
            query = query.filter(Book.author_id == author_id)
        
        return query
    
    @staticmethod
    def get_book_by_id(book_id: int) -> Book:
        """
        Get a specific book by ID
        
        Args:
            book_id: Book ID
            
        Returns:
            Book object
            
        Raises:
            BookNotFoundError: If book doesn't exist
        """
        book = db.session.get(Book, book_id)
        if not book:
            raise BookNotFoundError(book_id)
        return book
    
    @staticmethod
    def create_book(data: dict) -> Book:
        """
        Create a new book
        
        Args:
            data: Book data dictionary
            
        Returns:
            Created book object
            
        Raises:
            ValidationError: If data is invalid
            AuthorNotFoundError: If author doesn't exist
            DuplicateISBNError: If ISBN already exists
        """
        # Validate data
        BookValidator.validate_book_data(data)
        
        # Verify author exists
        BookService._verify_author_exists(data['author_id'])
        
        # Check for duplicate ISBN
        BookService._check_duplicate_isbn(data['isbn'])
        
        try:
            # Create book object
            book = BookService._create_book_object(data)
            
            # Add categories if provided
            if 'category_ids' in data and data['category_ids']:
                BookService._add_categories_to_book(book, data['category_ids'])
            
            db.session.add(book)
            db.session.commit()
            
            return book
            
        except IntegrityError:
            db.session.rollback()
            raise DuplicateISBNError(data['isbn'])
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create book: {str(e)}")
    
    @staticmethod
    def _create_book_object(data: dict) -> Book:
        """Create book object from data"""
        return Book(
            title=data['title'].strip(),
            isbn=data['isbn'],
            year=int(data['year']),
            author_id=data['author_id'],
            description=data.get('description', '').strip() if data.get('description') else None,
            pages=int(data['pages']) if data.get('pages') else None
        )
    
    @staticmethod
    def _verify_author_exists(author_id: int):
        """Verify that author exists"""
        author = db.session.get(Author, author_id)
        if not author:
            raise AuthorNotFoundError(author_id)
    
    @staticmethod
    def _check_duplicate_isbn(isbn: str, exclude_book_id: int = None):
        """Check for duplicate ISBN"""
        query = Book.query.filter_by(isbn=isbn)
        if exclude_book_id:
            query = query.filter(Book.id != exclude_book_id)
        
        existing = query.first()
        if existing:
            raise DuplicateISBNError(isbn)
    
    @staticmethod
    def _add_categories_to_book(book: Book, category_ids: list):
        """
        Add categories to book, validating that all IDs exist
        
        Args:
            book: Book object
            category_ids: List of category IDs
            
        Raises:
            ValidationError: If any category IDs don't exist
        """
        # Fetch all requested categories
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        
        # Check if all requested categories were found
        found_ids = {cat.id for cat in categories}
        requested_ids = set(category_ids)
        missing_ids = requested_ids - found_ids
        
        if missing_ids:
            raise ValidationError(
                f"Category IDs not found: {', '.join(map(str, missing_ids))}",
                field="category_ids"
            )
        
        book.categories.extend(categories)
    
    @staticmethod
    def update_book(book_id: int, data: dict) -> Book:
        """
        Update an existing book
        
        Args:
            book_id: Book ID
            data: Updated data
            
        Returns:
            Updated book object
        """
        # Validate data
        BookValidator.validate_book_data(data, is_update=True)
        
        # Get the book
        book = BookService.get_book_by_id(book_id)
        
        try:
            # Update basic fields
            BookService._update_book_fields(book, data)
            
            # Update categories if provided
            if 'category_ids' in data:
                # Remove existing categories by setting to empty list
                book.categories = []
                if data['category_ids']:
                    BookService._add_categories_to_book(book, data['category_ids'])
            
            db.session.commit()
            return book
            
        except IntegrityError:
            db.session.rollback()
            raise DuplicateISBNError(data.get('isbn', book.isbn))
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update book: {str(e)}")
    
    @staticmethod
    def _update_book_fields(book: Book, data: dict):
        """Update individual book fields from data"""
        if 'title' in data:
            book.title = data['title'].strip()
        
        if 'isbn' in data:
            if data['isbn'] != book.isbn:
                BookService._check_duplicate_isbn(data['isbn'], exclude_book_id=book.id)
            book.isbn = data['isbn']
        
        if 'year' in data:
            book.year = int(data['year'])
        
        if 'description' in data:
            book.description = data['description'].strip() if data['description'] else None
        
        if 'pages' in data:
            book.pages = int(data['pages']) if data['pages'] else None
        
        if 'author_id' in data:
            BookService._verify_author_exists(data['author_id'])
            book.author_id = data['author_id']
    
    @staticmethod
    def delete_book(book_id: int) -> Book:
        """
        Delete a book
        
        Args:
            book_id: Book ID
            
        Returns:
            Deleted book object
        """
        book = BookService.get_book_by_id(book_id)
        return BookService.safe_delete(book, "Failed to delete book")