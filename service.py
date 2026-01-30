"""
Book service layer - contains all business logic

This service layer:
- Separates business logic from HTTP/presentation concerns
- Returns data (not HTTP responses)
- Raises exceptions (doesn't format error messages)
- Can be reused in different contexts (CLI, API, tests)
- Makes the code testable without running Flask
"""

from typing import List, Optional
from models import Book
from validators import BookValidator
from exceptions import BookNotFoundError, DuplicateISBNError


class BookService:
    """
    Service layer for book management
    
    Handles all business logic without knowing about HTTP/Flask.
    This makes it:
    - Testable (no need to mock HTTP requests)
    - Reusable (can use in CLI, GUI, different API frameworks)
    - Maintainable (business rules in one place)
    """
    
    def __init__(self):
        """Initialize the book service with empty storage"""
        self._books: List[Book] = []
        self._next_id: int = 1
    
    def get_all_books(self) -> List[Book]:
        """
        Get all books
        
        Returns:
            List of all books
        """
        return self._books.copy()  # Return copy to prevent external modification
    
    def get_book_by_id(self, book_id: int) -> Book:
        """
        Get a specific book by ID
        
        Args:
            book_id: ID of the book to retrieve
            
        Returns:
            Book object
            
        Raises:
            BookNotFoundError: If book doesn't exist
        """
        for book in self._books:
            if book.id == book_id:
                return book
        
        raise BookNotFoundError(book_id)
    
    def create_book(self, data: dict) -> Book:
        """
        Create a new book
        
        Args:
            data: Dictionary containing book data
            
        Returns:
            Created Book object
            
        Raises:
            ValidationError: If data is invalid
            DuplicateISBNError: If ISBN already exists
        """
        # Validate the data
        BookValidator.validate_book_data(data, is_update=False)
        
        # Check for duplicate ISBN
        isbn = data['isbn']
        if self._isbn_exists(isbn):
            raise DuplicateISBNError(isbn)
        
        # Create the book
        book = Book(
            id=self._next_id,
            title=data['title'].strip(),
            author=data['author'].strip(),
            isbn=isbn,
            year=int(data['year'])
        )
        
        self._books.append(book)
        self._next_id += 1
        
        return book
    
    def update_book(self, book_id: int, data: dict) -> Book:
        """
        Update an existing book
        
        Args:
            book_id: ID of the book to update
            data: Dictionary containing fields to update
            
        Returns:
            Updated Book object
            
        Raises:
            BookNotFoundError: If book doesn't exist
            ValidationError: If data is invalid
            DuplicateISBNError: If ISBN already exists (when updating ISBN)
        """
        # Get the book (raises BookNotFoundError if not found)
        book = self.get_book_by_id(book_id)
        
        # Validate the update data
        BookValidator.validate_book_data(data, is_update=True)
        
        # Check for duplicate ISBN if ISBN is being updated
        if 'isbn' in data and data['isbn'] != book.isbn:
            if self._isbn_exists(data['isbn']):
                raise DuplicateISBNError(data['isbn'])
        
        # Prepare update data with proper types
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title'].strip()
        if 'author' in data:
            update_data['author'] = data['author'].strip()
        if 'isbn' in data:
            update_data['isbn'] = data['isbn']
        if 'year' in data:
            update_data['year'] = int(data['year'])
        
        # Update the book
        book.update(**update_data)
        
        return book
    
    def delete_book(self, book_id: int) -> Book:
        """
        Delete a book
        
        Args:
            book_id: ID of the book to delete
            
        Returns:
            Deleted Book object
            
        Raises:
            BookNotFoundError: If book doesn't exist
        """
        # Get the book (raises BookNotFoundError if not found)
        book = self.get_book_by_id(book_id)
        
        # Remove from storage
        self._books.remove(book)
        
        return book
    
    def _isbn_exists(self, isbn: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if an ISBN already exists
        
        Args:
            isbn: ISBN to check
            exclude_id: Optional book ID to exclude from check (for updates)
            
        Returns:
            True if ISBN exists, False otherwise
        """
        for book in self._books:
            if book.isbn == isbn and book.id != exclude_id:
                return True
        return False
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the book collection
        
        Returns:
            Dictionary with collection statistics
        """
        if not self._books:
            return {
                'total_books': 0,
                'earliest_year': None,
                'latest_year': None,
                'unique_authors': 0
            }
        
        years = [book.year for book in self._books]
        authors = {book.author for book in self._books}
        
        return {
            'total_books': len(self._books),
            'earliest_year': min(years),
            'latest_year': max(years),
            'unique_authors': len(authors)
        }
