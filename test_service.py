"""
Unit tests for BookService

This demonstrates the power of separating business logic:
- We can test business logic WITHOUT running Flask
- We can test WITHOUT making HTTP requests
- Tests are fast and focused
- Easy to test edge cases
"""

import unittest
from service import BookService
from exceptions import (
    BookNotFoundError,
    ValidationError,
    DuplicateISBNError
)


class TestBookService(unittest.TestCase):
    """Test suite for BookService"""
    
    def setUp(self):
        """Create a fresh service instance before each test"""
        self.service = BookService()
        
        # Sample valid book data
        self.valid_book_data = {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'year': 2008
        }
    
    # ==================== CREATE TESTS ====================
    
    def test_create_book_success(self):
        """Test successfully creating a book"""
        book = self.service.create_book(self.valid_book_data)
        
        self.assertEqual(book.title, 'Clean Code')
        self.assertEqual(book.author, 'Robert C. Martin')
        self.assertEqual(book.isbn, '9780132350884')
        self.assertEqual(book.year, 2008)
        self.assertEqual(book.id, 1)
        self.assertIsNotNone(book.created_at)
    
    def test_create_book_missing_title(self):
        """Test that creating a book without title raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['title']
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_book(invalid_data)
        
        self.assertIn('title', str(context.exception))
    
    def test_create_book_missing_author(self):
        """Test that creating a book without author raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        del invalid_data['author']
        
        with self.assertRaises(ValidationError):
            self.service.create_book(invalid_data)
    
    def test_create_book_invalid_year(self):
        """Test that invalid year raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['year'] = 2050  # Future year
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_book(invalid_data)
        
        self.assertIn('year', str(context.exception).lower())
    
    def test_create_book_invalid_isbn_format(self):
        """Test that invalid ISBN format raises ValidationError"""
        invalid_data = self.valid_book_data.copy()
        invalid_data['isbn'] = '123'  # Too short
        
        with self.assertRaises(ValidationError) as context:
            self.service.create_book(invalid_data)
        
        self.assertIn('isbn', str(context.exception).lower())
    
    def test_create_book_duplicate_isbn(self):
        """Test that duplicate ISBN raises DuplicateISBNError"""
        # Create first book
        self.service.create_book(self.valid_book_data)
        
        # Try to create another with same ISBN
        duplicate_data = {
            'title': 'Different Title',
            'author': 'Different Author',
            'isbn': '9780132350884',  # Same ISBN
            'year': 2020
        }
        
        with self.assertRaises(DuplicateISBNError) as context:
            self.service.create_book(duplicate_data)
        
        self.assertIn('9780132350884', str(context.exception))
    
    def test_create_multiple_books_increments_id(self):
        """Test that creating multiple books increments IDs correctly"""
        book1 = self.service.create_book(self.valid_book_data)
        
        book2_data = {
            'title': 'Another Book',
            'author': 'Another Author',
            'isbn': '9781234567890',
            'year': 2020
        }
        book2 = self.service.create_book(book2_data)
        
        self.assertEqual(book1.id, 1)
        self.assertEqual(book2.id, 2)
    
    # ==================== READ TESTS ====================
    
    def test_get_all_books_empty(self):
        """Test getting all books when none exist"""
        books = self.service.get_all_books()
        self.assertEqual(len(books), 0)
    
    def test_get_all_books_with_data(self):
        """Test getting all books when some exist"""
        self.service.create_book(self.valid_book_data)
        
        books = self.service.get_all_books()
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, 'Clean Code')
    
    def test_get_book_by_id_success(self):
        """Test successfully getting a book by ID"""
        created_book = self.service.create_book(self.valid_book_data)
        
        retrieved_book = self.service.get_book_by_id(created_book.id)
        
        self.assertEqual(retrieved_book.id, created_book.id)
        self.assertEqual(retrieved_book.title, created_book.title)
    
    def test_get_book_by_id_not_found(self):
        """Test that getting non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError) as context:
            self.service.get_book_by_id(999)
        
        self.assertEqual(context.exception.book_id, 999)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_book_title(self):
        """Test updating a book's title"""
        book = self.service.create_book(self.valid_book_data)
        
        updated_book = self.service.update_book(book.id, {'title': 'New Title'})
        
        self.assertEqual(updated_book.title, 'New Title')
        self.assertEqual(updated_book.author, 'Robert C. Martin')  # Unchanged
        self.assertIsNotNone(updated_book.updated_at)
    
    def test_update_book_multiple_fields(self):
        """Test updating multiple fields at once"""
        book = self.service.create_book(self.valid_book_data)
        
        update_data = {
            'title': 'Updated Title',
            'year': 2020
        }
        updated_book = self.service.update_book(book.id, update_data)
        
        self.assertEqual(updated_book.title, 'Updated Title')
        self.assertEqual(updated_book.year, 2020)
    
    def test_update_book_not_found(self):
        """Test that updating non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError):
            self.service.update_book(999, {'title': 'New Title'})
    
    def test_update_book_invalid_year(self):
        """Test that updating with invalid year raises ValidationError"""
        book = self.service.create_book(self.valid_book_data)
        
        with self.assertRaises(ValidationError):
            self.service.update_book(book.id, {'year': 3000})
    
    def test_update_book_duplicate_isbn(self):
        """Test that updating to duplicate ISBN raises DuplicateISBNError"""
        # Create two books
        book1 = self.service.create_book(self.valid_book_data)
        
        book2_data = {
            'title': 'Another Book',
            'author': 'Another Author',
            'isbn': '9781234567890',
            'year': 2020
        }
        book2 = self.service.create_book(book2_data)
        
        # Try to update book2's ISBN to match book1
        with self.assertRaises(DuplicateISBNError):
            self.service.update_book(book2.id, {'isbn': '9780132350884'})
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_book_success(self):
        """Test successfully deleting a book"""
        book = self.service.create_book(self.valid_book_data)
        
        deleted_book = self.service.delete_book(book.id)
        
        self.assertEqual(deleted_book.id, book.id)
        self.assertEqual(len(self.service.get_all_books()), 0)
    
    def test_delete_book_not_found(self):
        """Test that deleting non-existent book raises BookNotFoundError"""
        with self.assertRaises(BookNotFoundError):
            self.service.delete_book(999)
    
    def test_delete_book_actually_removes(self):
        """Test that deleted book is actually removed from storage"""
        book = self.service.create_book(self.valid_book_data)
        book_id = book.id
        
        self.service.delete_book(book_id)
        
        with self.assertRaises(BookNotFoundError):
            self.service.get_book_by_id(book_id)
    
    # ==================== STATISTICS TESTS ====================
    
    def test_statistics_empty_collection(self):
        """Test statistics with no books"""
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['total_books'], 0)
        self.assertIsNone(stats['earliest_year'])
        self.assertIsNone(stats['latest_year'])
        self.assertEqual(stats['unique_authors'], 0)
    
    def test_statistics_with_books(self):
        """Test statistics with multiple books"""
        # Create first book
        self.service.create_book(self.valid_book_data)
        
        # Create second book
        book2_data = {
            'title': 'The Pragmatic Programmer',
            'author': 'David Thomas',
            'isbn': '9780135957059',
            'year': 2019
        }
        self.service.create_book(book2_data)
        
        # Create third book with same author as first
        book3_data = {
            'title': 'Clean Architecture',
            'author': 'Robert C. Martin',  # Same as book 1
            'isbn': '9780134494166',
            'year': 2017
        }
        self.service.create_book(book3_data)
        
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['total_books'], 3)
        self.assertEqual(stats['earliest_year'], 2008)
        self.assertEqual(stats['latest_year'], 2019)
        self.assertEqual(stats['unique_authors'], 2)  # Robert C. Martin and David Thomas


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBookService)
    
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
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
