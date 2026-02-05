"""
Service layer with database operations

Handles all business logic with SQLAlchemy ORM.
Demonstrates:
- CRUD operations with database
- Complex queries (search, filter, pagination)
- JOIN operations
- Transaction management
"""

from typing import List, Optional, Dict
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import Book, Author, Category
from validators import BookValidator, AuthorValidator, CategoryValidator, PaginationValidator
from exceptions import (
    BookNotFoundError,
    AuthorNotFoundError,
    CategoryNotFoundError,
    DuplicateISBNError,
    DuplicateCategoryError,
    DatabaseError,
    ValidationError
)


class BookService:
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
        
        # Build query
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
            query = query.join(Book.categories).filter(Category.name.ilike(f"%{category}%"))
        
        # Apply year filter
        if year:
            query = query.filter(Book.year == year)
        
        # Apply author filter
        if author_id:
            query = query.filter(Book.author_id == author_id)
        
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
    def get_book_by_id(book_id: int) -> Book:
        """Get a specific book by ID"""
        book = db.session.get(Book, book_id)
        if not book:
            raise BookNotFoundError(book_id)
        return book
    
    @staticmethod
    def create_book(data: dict) -> Book:
        """Create a new book"""
        # Validate data
        BookValidator.validate_book_data(data)
        
        # Check if author exists
        author = db.session.get(Author, data['author_id'])
        if not author:
            raise AuthorNotFoundError(data['author_id'])
        
        # Check for duplicate ISBN
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            raise DuplicateISBNError(data['isbn'])
        
        try:
            # Create book
            book = Book(
                title=data['title'].strip(),
                isbn=data['isbn'],
                year=int(data['year']),
                author_id=data['author_id'],
                description=data.get('description', '').strip() if data.get('description') else None,
                pages=int(data['pages']) if data.get('pages') else None
            )
            
            # Add categories if provided
            if 'category_ids' in data and data['category_ids']:
                categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
                book.categories.extend(categories)
            
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
    def update_book(book_id: int, data: dict) -> Book:
        """Update an existing book"""
        # Validate data
        BookValidator.validate_book_data(data, is_update=True)
        
        # Get the book
        book = BookService.get_book_by_id(book_id)
        
        try:
            # Update fields
            if 'title' in data:
                book.title = data['title'].strip()
            if 'isbn' in data:
                # Check for duplicate ISBN
                if data['isbn'] != book.isbn:
                    existing = Book.query.filter_by(isbn=data['isbn']).first()
                    if existing:
                        raise DuplicateISBNError(data['isbn'])
                book.isbn = data['isbn']
            if 'year' in data:
                book.year = int(data['year'])
            if 'description' in data:
                book.description = data['description'].strip() if data['description'] else None
            if 'pages' in data:
                book.pages = int(data['pages']) if data['pages'] else None
            if 'author_id' in data:
                # Verify author exists
                author = db.session.get(Author, data['author_id'])
                if not author:
                    raise AuthorNotFoundError(data['author_id'])
                book.author_id = data['author_id']
            
            # Update categories if provided
            if 'category_ids' in data:
                book.categories.clear()
                if data['category_ids']:
                    categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
                    book.categories.extend(categories)
            
            db.session.commit()
            return book
            
        except IntegrityError:
            db.session.rollback()
            raise DuplicateISBNError(data.get('isbn', book.isbn))
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update book: {str(e)}")
    
    @staticmethod
    def delete_book(book_id: int) -> Book:
        """Delete a book"""
        book = BookService.get_book_by_id(book_id)
        
        try:
            db.session.delete(book)
            db.session.commit()
            return book
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete book: {str(e)}")


class AuthorService:
    """Service for author operations"""
    
    @staticmethod
    def get_all_authors(page: int = 1, per_page: int = 10) -> Dict:
        """Get all authors with pagination"""
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
        """Get a specific author by ID"""
        author = db.session.get(Author, author_id)
        if not author:
            raise AuthorNotFoundError(author_id)
        return author
    
    @staticmethod
    def create_author(data: dict) -> Author:
        """Create a new author"""
        AuthorValidator.validate_author_data(data)
        
        try:
            author = Author(
                name=data['name'].strip(),
                bio=data.get('bio', '').strip() if data.get('bio') else None,
                country=data.get('country', '').strip() if data.get('country') else None
            )
            
            db.session.add(author)
            db.session.commit()
            return author
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create author: {str(e)}")
    
    @staticmethod
    def update_author(author_id: int, data: dict) -> Author:
        """Update an existing author"""
        AuthorValidator.validate_author_data(data, is_update=True)
        
        author = AuthorService.get_author_by_id(author_id)
        
        try:
            if 'name' in data:
                author.name = data['name'].strip()
            if 'bio' in data:
                author.bio = data['bio'].strip() if data['bio'] else None
            if 'country' in data:
                author.country = data['country'].strip() if data['country'] else None
            
            db.session.commit()
            return author
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update author: {str(e)}")
    
    @staticmethod
    def delete_author(author_id: int) -> Author:
        """Delete an author (will fail if author has books due to foreign key)"""
        author = AuthorService.get_author_by_id(author_id)
        
        # Check if author has books
        if author.books.count() > 0:
            raise ValidationError(
                f"Cannot delete author with existing books. Delete {author.books.count()} book(s) first."
            )
        
        try:
            db.session.delete(author)
            db.session.commit()
            return author
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete author: {str(e)}")


class CategoryService:
    """Service for category operations"""
    
    @staticmethod
    def get_all_categories() -> List[Category]:
        """Get all categories"""
        try:
            return Category.query.order_by(Category.name).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch categories: {str(e)}")
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Category:
        """Get a specific category by ID"""
        category = db.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        return category
    
    @staticmethod
    def create_category(data: dict) -> Category:
        """Create a new category"""
        CategoryValidator.validate_category_data(data)
        
        # Check for duplicate
        existing = Category.query.filter_by(name=data['name'].strip()).first()
        if existing:
            raise DuplicateCategoryError(data['name'])
        
        try:
            category = Category(
                name=data['name'].strip(),
                description=data.get('description', '').strip() if data.get('description') else None
            )
            
            db.session.add(category)
            db.session.commit()
            return category
            
        except IntegrityError:
            db.session.rollback()
            raise DuplicateCategoryError(data['name'])
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create category: {str(e)}")
    
    @staticmethod
    def delete_category(category_id: int) -> Category:
        """Delete a category"""
        category = CategoryService.get_category_by_id(category_id)
        
        try:
            db.session.delete(category)
            db.session.commit()
            return category
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete category: {str(e)}")
