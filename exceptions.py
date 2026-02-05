"""
Custom exceptions for the Book Library API

Provides clear error types for different failure scenarios.
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
    def __init__(self, book_id: int = None):
        self.book_id = book_id
        self.message = f"Book with ID {book_id} not found" if book_id else "Book not found"
        super().__init__(self.message)


class AuthorNotFoundError(BookLibraryError):
    """Raised when a requested author doesn't exist"""
    def __init__(self, author_id: int = None):
        self.author_id = author_id
        self.message = f"Author with ID {author_id} not found" if author_id else "Author not found"
        super().__init__(self.message)


class CategoryNotFoundError(BookLibraryError):
    """Raised when a requested category doesn't exist"""
    def __init__(self, category_id: int = None):
        self.category_id = category_id
        self.message = f"Category with ID {category_id} not found" if category_id else "Category not found"
        super().__init__(self.message)


class DuplicateISBNError(BookLibraryError):
    """Raised when attempting to create a book with duplicate ISBN"""
    def __init__(self, isbn: str):
        self.isbn = isbn
        self.message = f"A book with ISBN {isbn} already exists"
        super().__init__(self.message)


class DuplicateCategoryError(BookLibraryError):
    """Raised when attempting to create a duplicate category"""
    def __init__(self, name: str):
        self.name = name
        self.message = f"Category '{name}' already exists"
        super().__init__(self.message)


class DatabaseError(BookLibraryError):
    """Raised when a database operation fails"""
    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)
