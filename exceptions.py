"""
Custom exceptions for the Book Library API

Using custom exceptions provides:
- Clear error semantics
- Better separation of business logic from HTTP responses
- Easier testing
- Centralized error handling
"""


class BookLibraryError(Exception):
    """Base exception for all book library errors"""
    pass


class ValidationError(BookLibraryError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class BookNotFoundError(BookLibraryError):
    """Raised when a requested book doesn't exist"""
    def __init__(self, book_id: int):
        self.book_id = book_id
        self.message = f"Book with ID {book_id} not found"
        super().__init__(self.message)


class DuplicateISBNError(BookLibraryError):
    """Raised when attempting to create a book with duplicate ISBN"""
    def __init__(self, isbn: str):
        self.isbn = isbn
        self.message = f"A book with ISBN {isbn} already exists"
        super().__init__(self.message)


class InvalidDataFormatError(BookLibraryError):
    """Raised when request data format is invalid"""
    def __init__(self, message: str = "Invalid data format"):
        self.message = message
        super().__init__(self.message)
