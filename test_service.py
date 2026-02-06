"""
Unit tests for Service Layer with Database

This demonstrates proper testing with a real database:
- Uses a separate test database (SQLite in-memory)
- Sets up Flask app context for each test
- Cleans up database between tests
- Tests business logic WITHOUT making HTTP requests
- Fast and focused tests
"""

import unittest
import os
import tempfile
from app import create_app
from database import db
from models import Book, Author, Category
from services import BookService, AuthorService, CategoryService
from exceptions import (
    BookNotFoundError,
    AuthorNotFoundError,
    CategoryNotFoundError,
    ValidationError,
    DuplicateISBNError,
    DuplicateCategoryError,
    DatabaseError
)


class BaseTestCase(unittest.TestCase):
    """Base test case with database setup and teardown"""
    
    def setUp(self):
        """Set up test database before each test"""
        # Create a temporary file for the test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configure app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all tables
        db.create_all()
        
        # Create a test client (for integration tests if needed)
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove database session
        db.session.remove()
        
        # Drop all tables
        db.drop_all()
        
        # Pop application context
        self.app_context.pop()
        
        # Close and remove the temporary database file
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def create_test_author(self, name="Test Author", bio="Test bio", country="Test Country"):
        """Helper method to create a test author"""
        author = Author(name=name, bio=bio, country=country)
        db.session.add(author)
        db.session.commit()
        return author
    
    def create_test_category(self, name=None, description="Test description"):
        """Helper method to create a test category"""
        if name is None:
            name = f"Test Category {os.getpid()}"  # Use process ID to ensure uniqueness
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category
    
    def create_test_book(self, title="Test Book", isbn="1234567890", 
                        year=2020, author=None, categories=None):
        """Helper method to create a test book"""
        if author is None:
            author = self.create_test_author()
        
        book = Book(
            title=title,
            isbn=isbn,
            year=year,
            author_id=author.id,
            description="Test description",
            pages=100
        )
        
        if categories:
            book.categories.extend(categories)
        
        db.session.add(book)
        db.session.commit()
        return book


class TestBookService(BaseTestCase):
    """Test suite for BookService"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        # Create test author and category
        self.author = self.create_test_author(
            name="Robert C. Martin",
            bio="Software engineer",
            country="USA"
        )
        self.category = self.create_test_category(
            name="Programming",
            description="Software development books"
        )
        
        # Sample valid book data
        self.valid_book_data = {
            'title': 'Clean Code',
            'isbn': '9780132350884',
            'year': 2008,
            'author_id': self.author.id,
            'description': 'A handbook of agile software craftsmanship',
            'pages': 464,
            'category_ids': [self.category.id]
        }
    
    # ==================== CREATE TESTS ====================
    
    def test_create_book_success(self):
        """Test successfully creating a book"""
        book = BookService.create_book(self.valid_book_data)
        
        self.assertEqual(book.title, 'Clean Code')
        self.assertEqual(book.isbn, '9780132350884')
        self.assertEqual(book.year, 2008)
        self.assertEqual(book.author_id, self.author.id)
        self.assertEqual(book.description, 'A handbook of agile software craftsmanship')
        self.assertEqual(book.pages, 464)
        self.assertIsNotNone(book.created_at)
        self.assertEqual(len(list(book.categories)), 1)
        self.assertEqual(list(book.categories)[0].name, 'Programming')
    
    def test_create_book_missing_title(self):
        """Test that creating a book without title raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['title']
        
        with self.assertRaises(ValidationError) as context:
            BookService.create_book(invalid_data)
        
        self.assertIn('title', str(context.exception).lower())
    
    def test_create_book_missing_isbn(self):
        """Test that creating a book without ISBN raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['isbn']
        
        with self.assertRaises(ValidationError) as context:
            BookService.create_book(invalid_data)
        
        self.assertIn('isbn', str(context.exception).lower())
    
    def test_create_book_missing_year(self):
        """Test that creating a book without year raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['year']
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_missing_author_id(self):
        """Test that creating a book without author_id raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['author_id']
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_invalid_year_future(self):
        """Test that future year raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['year'] = 2050  # Future year
        
        with self.assertRaises(ValidationError) as context:
            BookService.create_book(invalid_data)
        
        self.assertIn('year', str(context.exception).lower())
    
    def test_create_book_invalid_year_too_old(self):
        """Test that year before 1000 raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['year'] = 999
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_invalid_isbn_format(self):
        """Test that invalid ISBN format raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['isbn'] = '123'  # Too short
        
        with self.assertRaises(ValidationError) as context:
            BookService.create_book(invalid_data)
        
        self.assertIn('isbn', str(context.exception).lower())
    
    def test_create_book_invalid_isbn_non_numeric(self):
        """Test that non-numeric ISBN raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['isbn'] = 'ABC1234567'
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_duplicate_isbn(self):
        """Test that duplicate ISBN raises DuplicateISBNError"""
        # Create first book
        BookService.create_book(self.valid_book_data)
        
        # Try to create another with same ISBN
        duplicate_data = self.valid_book_data.copy()
        duplicate_data['title'] = 'Different Title'
        
        with self.assertRaises(DuplicateISBNError) as context:
            BookService.create_book(duplicate_data)
        
        self.assertIn('9780132350884', str(context.exception))
    
    def test_create_book_invalid_author(self):
        """Test that invalid author_id raises AuthorNotFoundError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['author_id'] = 9999  # Non-existent
        
        with self.assertRaises(AuthorNotFoundError):
            BookService.create_book(invalid_data)
    
    def test_create_book_invalid_pages_negative(self):
        """Test that negative pages raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['pages'] = -10
        
        with self.assertRaises(ValidationError) as context:
            BookService.create_book(invalid_data)
        
        self.assertIn('pages', str(context.exception).lower())
    
    def test_create_book_invalid_pages_zero(self):
        """Test that zero pages raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['pages'] = 0
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_empty_title(self):
        """Test that empty title raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['title'] = '   '  # Whitespace only
        
        with self.assertRaises(ValidationError):
            BookService.create_book(invalid_data)
    
    def test_create_book_without_categories(self):
        """Test creating a book without categories"""
        data = self.valid_book_data.copy()
        del data['category_ids']
        
        book = BookService.create_book(data)
        self.assertEqual(len(list(book.categories)), 0)
    
    def test_create_book_multiple_categories(self):
        """Test creating a book with multiple categories"""
        category2 = self.create_test_category(name="Science", description="Science books")
        
        data = self.valid_book_data.copy()
        data['category_ids'] = [self.category.id, category2.id]
        
        book = BookService.create_book(data)
        self.assertEqual(len(list(book.categories)), 2)
    
    # ==================== READ TESTS ====================
    
    def test_get_all_books_empty(self):
        """Test getting all books when none exist"""
        result = BookService.get_all_books()
        
        self.assertEqual(len(result['books']), 0)
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['page'], 1)
    
    def test_get_all_books_with_data(self):
        """Test getting all books when some exist"""
        BookService.create_book(self.valid_book_data)
        
        result = BookService.get_all_books()
        
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['books'][0]['title'], 'Clean Code')
    
    def test_get_book_by_id_success(self):
        """Test successfully getting a book by ID"""
        created_book = BookService.create_book(self.valid_book_data)
        
        retrieved_book = BookService.get_book_by_id(created_book.id)
        
        self.assertEqual(retrieved_book.id, created_book.id)
        self.assertEqual(retrieved_book.title, created_book.title)
        self.assertEqual(retrieved_book.isbn, created_book.isbn)
    
    def test_get_book_by_id_not_found(self):
        """Test that getting non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError) as context:
            BookService.get_book_by_id(999)
        
        self.assertEqual(context.exception.book_id, 999)
    
    def test_get_all_books_with_pagination(self):
        """Test pagination"""
        # Create 5 books
        for i in range(5):
            data = self.valid_book_data.copy()
            data['isbn'] = f'123456789{i}'
            data['title'] = f'Book {i}'
            BookService.create_book(data)
        
        # Get first page (2 per page)
        result = BookService.get_all_books(page=1, per_page=2)
        
        self.assertEqual(len(result['books']), 2)
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['pages'], 3)
        self.assertTrue(result['has_next'])
        self.assertFalse(result['has_prev'])
    
    def test_get_all_books_with_search(self):
        """Test search functionality"""
        # Create books with different titles and authors
        BookService.create_book(self.valid_book_data)
        
        author2 = self.create_test_author(name="George Orwell")
        data2 = {
            'title': '1984',
            'isbn': '9780451524935',
            'year': 1949,
            'author_id': author2.id
        }
        BookService.create_book(data2)
        
        # Search by title
        result = BookService.get_all_books(search='clean')
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['title'], 'Clean Code')
        
        # Search by author
        result = BookService.get_all_books(search='orwell')
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['title'], '1984')
    
    def test_get_all_books_filter_by_category(self):
        """Test filtering by category"""
        BookService.create_book(self.valid_book_data)
        
        fiction = self.create_test_category(name="Fiction")
        data2 = {
            'title': 'Another Book',
            'isbn': '1234567891',
            'year': 2020,
            'author_id': self.author.id,
            'category_ids': [fiction.id]
        }
        BookService.create_book(data2)
        
        result = BookService.get_all_books(category='Programming')
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['title'], 'Clean Code')
    
    def test_get_all_books_filter_by_year(self):
        """Test filtering by year"""
        BookService.create_book(self.valid_book_data)
        
        data2 = self.valid_book_data.copy()
        data2['isbn'] = '1234567891'
        data2['title'] = 'Another Book'
        data2['year'] = 2020
        BookService.create_book(data2)
        
        result = BookService.get_all_books(year=2008)
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['year'], 2008)
    
    def test_get_all_books_filter_by_author(self):
        """Test filtering by author ID"""
        BookService.create_book(self.valid_book_data)
        
        author2 = self.create_test_author(name="Another Author")
        data2 = {
            'title': 'Another Book',
            'isbn': '1234567891',
            'year': 2020,
            'author_id': author2.id
        }
        BookService.create_book(data2)
        
        result = BookService.get_all_books(author_id=self.author.id)
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['author']['name'], 'Robert C. Martin')
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_book_title(self):
        """Test updating a book's title"""
        book = BookService.create_book(self.valid_book_data)
        
        updated_book = BookService.update_book(book.id, {'title': 'New Title'})
        
        self.assertEqual(updated_book.title, 'New Title')
        self.assertEqual(updated_book.isbn, '9780132350884')  # Unchanged
        self.assertIsNotNone(updated_book.updated_at)
    
    def test_update_book_multiple_fields(self):
        """Test updating multiple fields at once"""
        book = BookService.create_book(self.valid_book_data)
        
        update_data = {
            'title': 'Updated Title',
            'year': 2023,
            'pages': 500
        }
        updated_book = BookService.update_book(book.id, update_data)
        
        self.assertEqual(updated_book.title, 'Updated Title')
        self.assertEqual(updated_book.year, 2023)
        self.assertEqual(updated_book.pages, 500)
    
    def test_update_book_categories(self):
        """Test updating book categories"""
        book = BookService.create_book(self.valid_book_data)
        
        category2 = self.create_test_category(name="Science")
        update_data = {'category_ids': [category2.id]}
        
        updated_book = BookService.update_book(book.id, update_data)
        
        self.assertEqual(len(list(updated_book.categories)), 1)
        self.assertEqual(list(updated_book.categories)[0].name, 'Science')
    
    def test_update_book_not_found(self):
        """Test that updating non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError):
            BookService.update_book(999, {'title': 'New Title'})
    
    def test_update_book_invalid_year(self):
        """Test that updating with invalid year raises ValidationError"""
        book = BookService.create_book(self.valid_book_data)
        
        with self.assertRaises(ValidationError):
            BookService.update_book(book.id, {'year': 3000})
    
    def test_update_book_duplicate_isbn(self):
        """Test that updating to duplicate ISBN raises DuplicateISBNError"""
        book1 = BookService.create_book(self.valid_book_data)
        
        data2 = self.valid_book_data.copy()
        data2['isbn'] = '9781234567890'
        data2['title'] = 'Another Book'
        book2 = BookService.create_book(data2)
        
        # Try to update book2's ISBN to match book1
        with self.assertRaises(DuplicateISBNError):
            BookService.update_book(book2.id, {'isbn': '9780132350884'})
    
    def test_update_book_invalid_author(self):
        """Test updating with non-existent author"""
        book = BookService.create_book(self.valid_book_data)
        
        with self.assertRaises(AuthorNotFoundError):
            BookService.update_book(book.id, {'author_id': 9999})
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_book_success(self):
        """Test successfully deleting a book"""
        book = BookService.create_book(self.valid_book_data)
        
        deleted_book = BookService.delete_book(book.id)
        
        self.assertEqual(deleted_book.id, book.id)
        
        # Verify it's actually deleted
        result = BookService.get_all_books()
        self.assertEqual(len(result['books']), 0)
    
    def test_delete_book_not_found(self):
        """Test that deleting non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError):
            BookService.delete_book(999)
    
    def test_delete_book_actually_removes(self):
        """Test that deleted book is actually removed from database"""
        book = BookService.create_book(self.valid_book_data)
        book_id = book.id
        
        BookService.delete_book(book_id)
        
        with self.assertRaises(BookNotFoundError):
            BookService.get_book_by_id(book_id)


class TestAuthorService(BaseTestCase):
    """Test suite for AuthorService"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        self.valid_author_data = {
            'name': 'Robert C. Martin',
            'bio': 'Software engineer and author',
            'country': 'USA'
        }
    
    def test_create_author_success(self):
        """Test successfully creating an author"""
        author = AuthorService.create_author(self.valid_author_data)
        
        self.assertEqual(author.name, 'Robert C. Martin')
        self.assertEqual(author.bio, 'Software engineer and author')
        self.assertEqual(author.country, 'USA')
        self.assertIsNotNone(author.created_at)
    
    def test_create_author_missing_name(self):
        """Test creating author without name raises ValidationError"""
        invalid_data = {}
        
        with self.assertRaises(ValidationError):
            AuthorService.create_author(invalid_data)
    
    def test_create_author_empty_name(self):
        """Test creating author with empty name raises ValidationError"""
        invalid_data = {'name': '   '}
        
        with self.assertRaises(ValidationError):
            AuthorService.create_author(invalid_data)
    
    def test_create_author_name_too_long(self):
        """Test creating author with name > 200 chars raises ValidationError"""
        invalid_data = {'name': 'A' * 201}
        
        with self.assertRaises(ValidationError):
            AuthorService.create_author(invalid_data)
    
    def test_get_author_by_id_success(self):
        """Test getting author by ID"""
        created_author = AuthorService.create_author(self.valid_author_data)
        
        retrieved_author = AuthorService.get_author_by_id(created_author.id)
        
        self.assertEqual(retrieved_author.id, created_author.id)
        self.assertEqual(retrieved_author.name, created_author.name)
    
    def test_get_author_by_id_not_found(self):
        """Test getting non-existent author raises AuthorNotFoundError"""
        with self.assertRaises(AuthorNotFoundError):
            AuthorService.get_author_by_id(999)
    
    def test_get_all_authors_with_pagination(self):
        """Test getting all authors with pagination"""
        for i in range(5):
            data = {'name': f'Author {i}'}
            AuthorService.create_author(data)
        
        result = AuthorService.get_all_authors(page=1, per_page=2)
        
        self.assertEqual(len(result['authors']), 2)
        self.assertEqual(result['total'], 5)
    
    def test_update_author_success(self):
        """Test updating an author"""
        author = AuthorService.create_author(self.valid_author_data)
        
        updated_author = AuthorService.update_author(
            author.id,
            {'bio': 'Updated biography'}
        )
        
        self.assertEqual(updated_author.bio, 'Updated biography')
        self.assertEqual(updated_author.name, 'Robert C. Martin')
    
    def test_delete_author_without_books(self):
        """Test deleting author without books succeeds"""
        author = AuthorService.create_author(self.valid_author_data)
        
        deleted_author = AuthorService.delete_author(author.id)
        
        self.assertEqual(deleted_author.id, author.id)
    
    def test_delete_author_with_books_fails(self):
        """Test that deleting author with books raises ValidationError"""
        author = self.create_test_author()
        self.create_test_book(author=author)
        
        with self.assertRaises(ValidationError) as context:
            AuthorService.delete_author(author.id)
        
        self.assertIn('book', str(context.exception).lower())


class TestCategoryService(BaseTestCase):
    """Test suite for CategoryService"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        self.valid_category_data = {
            'name': f'Programming {os.getpid()}',
            'description': 'Software development books'
        }
    
    def test_create_category_success(self):
        """Test successfully creating a category"""
        category = CategoryService.create_category(self.valid_category_data)
        
        self.assertEqual(category.description, 'Software development books')
        self.assertIsNotNone(category.created_at)
    
    def test_create_category_missing_name(self):
        """Test creating category without name raises ValidationError"""
        with self.assertRaises(ValidationError):
            CategoryService.create_category({})
    
    def test_create_category_empty_name(self):
        """Test creating category with empty name raises ValidationError"""
        with self.assertRaises(ValidationError):
            CategoryService.create_category({'name': '   '})
    
    def test_create_category_duplicate_name(self):
        """Test creating duplicate category raises DuplicateCategoryError"""
        CategoryService.create_category(self.valid_category_data)
        
        with self.assertRaises(DuplicateCategoryError):
            CategoryService.create_category(self.valid_category_data)
    
    def test_create_category_name_too_long(self):
        """Test creating category with name > 100 chars raises ValidationError"""
        invalid_data = {'name': 'A' * 101}
        
        with self.assertRaises(ValidationError):
            CategoryService.create_category(invalid_data)
    
    def test_get_category_by_id_success(self):
        """Test getting category by ID"""
        created_category = CategoryService.create_category(self.valid_category_data)
        
        retrieved_category = CategoryService.get_category_by_id(created_category.id)
        
        self.assertEqual(retrieved_category.id, created_category.id)
        self.assertEqual(retrieved_category.name, created_category.name)
    
    def test_get_category_by_id_not_found(self):
        """Test getting non-existent category raises CategoryNotFoundError"""
        with self.assertRaises(CategoryNotFoundError):
            CategoryService.get_category_by_id(999)
    
    def test_get_all_categories(self):
        """Test getting all categories"""
        CategoryService.create_category(self.valid_category_data)
        CategoryService.create_category({'name': 'Fiction'})
        
        categories = CategoryService.get_all_categories()
        
        self.assertEqual(len(categories), 2)
    
    def test_delete_category_success(self):
        """Test deleting a category"""
        category = CategoryService.create_category(self.valid_category_data)
        
        deleted_category = CategoryService.delete_category(category.id)
        
        self.assertEqual(deleted_category.id, category.id)


class TestPaginationValidation(BaseTestCase):
    """Test pagination validation"""
    
    def test_invalid_page_zero(self):
        """Test that page=0 raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            BookService.get_all_books(page=0)
        
        self.assertIn('page', str(context.exception).lower())
    
    def test_invalid_page_negative(self):
        """Test that negative page raises ValidationError"""
        with self.assertRaises(ValidationError):
            BookService.get_all_books(page=-1)
    
    def test_invalid_per_page_zero(self):
        """Test that per_page=0 raises ValidationError"""
        with self.assertRaises(ValidationError):
            BookService.get_all_books(per_page=0)
    
    def test_invalid_per_page_too_large(self):
        """Test that per_page>100 raises ValidationError"""
        with self.assertRaises(ValidationError):
            BookService.get_all_books(per_page=101)


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBookService))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorService))
    suite.addTests(loader.loadTestsFromTestCase(TestCategoryService))
    suite.addTests(loader.loadTestsFromTestCase(TestPaginationValidation))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()