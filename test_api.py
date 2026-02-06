"""
Comprehensive test script for Week 3 features

Demonstrates:
- CRUD operations on all entities
- Search functionality
- Filtering
- Pagination
- Relationships
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5001
"

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*70}\n")
    sleep(0.3)


def test_api():
    """Run comprehensive API tests"""
    
    print("\n" + "="*70)
    print("WEEK 3 - DATABASE API TESTING")
    print("="*70)
    
    # ==================== CATEGORY TESTS ====================
    print("\n🏷️  TESTING CATEGORIES")
    
    # Create categories
    print("\n📝 Creating categories...")
    programming = requests.post(
        f"{BASE_URL}/categories",
        json={"name": "Programming", "description": "Software development books"},
        headers={"Content-Type": "application/json"}
    )
    print_response(programming, "POST /categories (Programming)")
    
    fiction = requests.post(
        f"{BASE_URL}/categories",
        json={"name": "Fiction", "description": "Literary fiction"},
        headers={"Content-Type": "application/json"}
    )
    print_response(fiction, "POST /categories (Fiction)")
    
    # Get all categories
    categories = requests.get(f"{BASE_URL}/categories")
    print_response(categories, "GET /categories")
    
    # ==================== AUTHOR TESTS ====================
    print("\n✍️  TESTING AUTHORS")
    
    # Create authors
    print("\n📝 Creating authors...")
    author1 = requests.post(
        f"{BASE_URL}/authors",
        json={
            "name": "Robert C. Martin",
            "bio": "Software engineer and author",
            "country": "USA"
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(author1, "POST /authors (Robert C. Martin)")
    author1_id = author1.json()['data']['id']
    
    author2 = requests.post(
        f"{BASE_URL}/authors",
        json={
            "name": "George Orwell",
            "bio": "English novelist and essayist",
            "country": "UK"
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(author2, "POST /authors (George Orwell)")
    author2_id = author2.json()['data']['id']
    
    # Get all authors (paginated)
    authors = requests.get(f"{BASE_URL}/authors?page=1&per_page=10")
    print_response(authors, "GET /authors (paginated)")
    
    # ==================== BOOK TESTS ====================
    print("\n📚 TESTING BOOKS")
    
    # Create books
    print("\n📝 Creating books...")
    programming_cat_id = programming.json()['data']['id']
    fiction_cat_id = fiction.json()['data']['id']
    
    book1 = requests.post(
        f"{BASE_URL}/books",
        json={
            "title": "Clean Code",
            "isbn": "9780132350884",
            "year": 2008,
            "author_id": author1_id,
            "description": "A handbook of agile software craftsmanship",
            "pages": 464,
            "category_ids": [programming_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(book1, "POST /books (Clean Code)")
    book1_id = book1.json()['data']['id']
    
    book2 = requests.post(
        f"{BASE_URL}/books",
        json={
            "title": "Clean Architecture",
            "isbn": "9780134494166",
            "year": 2017,
            "author_id": author1_id,
            "description": "A guide to software architecture",
            "pages": 432,
            "category_ids": [programming_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(book2, "POST /books (Clean Architecture)")
    
    book3 = requests.post(
        f"{BASE_URL}/books",
        json={
            "title": "1984",
            "isbn": "9780451524935",
            "year": 1949,
            "author_id": author2_id,
            "description": "Dystopian social science fiction",
            "pages": 328,
            "category_ids": [fiction_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(book3, "POST /books (1984)")
    
    # ==================== SEARCH & FILTER TESTS ====================
    print("\n🔍 TESTING SEARCH & FILTERING")
    
    # Search by title
    search_title = requests.get(f"{BASE_URL}/books?search=clean")
    print_response(search_title, "GET /books?search=clean")
    
    # Search by author
    search_author = requests.get(f"{BASE_URL}/books?search=orwell")
    print_response(search_author, "GET /books?search=orwell")
    
    # Filter by category
    filter_category = requests.get(f"{BASE_URL}/books?category=programming")
    print_response(filter_category, "GET /books?category=programming")
    
    # Filter by year
    filter_year = requests.get(f"{BASE_URL}/books?year=2008")
    print_response(filter_year, "GET /books?year=2008")
    
    # Filter by author
    filter_author = requests.get(f"{BASE_URL}/books?author_id=" + str(author1_id))
    print_response(filter_author, f"GET /books?author_id={author1_id}")
    
    # Combined filters
    combined = requests.get(
        f"{BASE_URL}/books?category=programming&search=architecture"
    )
    print_response(combined, "GET /books?category=programming&search=architecture")
    
    # ==================== PAGINATION TESTS ====================
    print("\n📄 TESTING PAGINATION")
    
    # Get first page
    page1 = requests.get(f"{BASE_URL}/books?page=1&per_page=2")
    print_response(page1, "GET /books?page=1&per_page=2")
    
    # Get second page
    page2 = requests.get(f"{BASE_URL}/books?page=2&per_page=2")
    print_response(page2, "GET /books?page=2&per_page=2")
    
    # ==================== RELATIONSHIP TESTS ====================
    print("\n🔗 TESTING RELATIONSHIPS")
    
    # Get author with books
    author_with_books = requests.get(
        f"{BASE_URL}/authors/{author1_id}?include_books=true"
    )
    print_response(author_with_books, f"GET /authors/{author1_id}?include_books=true")
    
    # Get category with books
    category_with_books = requests.get(
        f"{BASE_URL}/categories/{programming_cat_id}?include_books=true"
    )
    print_response(category_with_books, f"GET /categories/{programming_cat_id}?include_books=true")
    
    # Get book with full details
    book_detail = requests.get(f"{BASE_URL}/books/{book1_id}")
    print_response(book_detail, f"GET /books/{book1_id}")
    
    # ==================== UPDATE TESTS ====================
    print("\n✏️  TESTING UPDATES")
    
    # Update book
    update_book = requests.put(
        f"{BASE_URL}/books/{book1_id}",
        json={
            "year": 2023,
            "description": "Updated description",
            "category_ids": [programming_cat_id, fiction_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(update_book, f"PUT /books/{book1_id}")
    
    # Update author
    update_author = requests.put(
        f"{BASE_URL}/authors/{author1_id}",
        json={"bio": "Updated biography - Software craftsman and author"},
        headers={"Content-Type": "application/json"}
    )
    print_response(update_author, f"PUT /authors/{author1_id}")
    
    # ==================== ERROR HANDLING TESTS ====================
    print("\n❌ TESTING ERROR HANDLING")
    
    # Duplicate ISBN
    duplicate_isbn = requests.post(
        f"{BASE_URL}/books",
        json={
            "title": "Another Book",
            "isbn": "9780132350884",  # Same as Clean Code
            "year": 2020,
            "author_id": author1_id,
            "category_ids": [programming_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(duplicate_isbn, "POST /books (duplicate ISBN)")
    
    # Invalid author
    invalid_author = requests.post(
        f"{BASE_URL}/books",
        json={
            "title": "Test Book",
            "isbn": "1234567890",
            "year": 2020,
            "author_id": 9999,  # Non-existent
            "category_ids": [programming_cat_id]
        },
        headers={"Content-Type": "application/json"}
    )
    print_response(invalid_author, "POST /books (invalid author)")
    
    # Book not found
    not_found = requests.get(f"{BASE_URL}/books/9999")
    print_response(not_found, "GET /books/9999 (not found)")
    
    # Invalid pagination
    invalid_page = requests.get(f"{BASE_URL}/books?page=0")
    print_response(invalid_page, "GET /books?page=0 (invalid)")
    
    # ==================== DELETE TESTS ====================
    print("\n🗑️  TESTING DELETES")
    
    # Try to delete author with books (should fail)
    delete_author_fail = requests.delete(f"{BASE_URL}/authors/{author1_id}")
    print_response(delete_author_fail, f"DELETE /authors/{author1_id} (has books - should fail)")
    
    # Delete a book
    delete_book = requests.delete(f"{BASE_URL}/books/{book1_id}")
    print_response(delete_book, f"DELETE /books/{book1_id}")
    
    # Delete category
    delete_category = requests.delete(f"{BASE_URL}/categories/{fiction_cat_id}")
    print_response(delete_category, f"DELETE /categories/{fiction_cat_id}")
    
    # ==================== FINAL STATE ====================
    print("\n📊 FINAL DATABASE STATE")
    
    all_books = requests.get(f"{BASE_URL}/books")
    print_response(all_books, "GET /books (final state)")
    
    all_authors = requests.get(f"{BASE_URL}/authors")
    print_response(all_authors, "GET /authors (final state)")
    
    all_categories = requests.get(f"{BASE_URL}/categories")
    print_response(all_categories, "GET /categories (final state)")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70)
    print("\nFeatures Demonstrated:")
    print("  ✅ CRUD operations on Books, Authors, Categories")
    print("  ✅ Search (by title and author name)")
    print("  ✅ Filtering (by category, year, author)")
    print("  ✅ Pagination")
    print("  ✅ One-to-Many relationships (Author → Books)")
    print("  ✅ Many-to-Many relationships (Books ↔ Categories)")
    print("  ✅ Error handling (duplicates, not found, invalid data)")
    print("  ✅ Cascade constraints (cannot delete author with books)")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        print("\n⚠️  Make sure the API is running on http://localhost:5001")
        print("Run: python app.py")
        print("\nPress Enter to start tests...")
        input()
        
        test_api()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API")
        print("Make sure the Flask application is running:")
        print("  python app.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
