# Book Library API - Week 2 Project

A professionally architected RESTful API for managing a book collection, built with clean architecture principles and industry best practices.

## 🎯 Project Overview

This project demonstrates a production-ready Flask API that goes beyond basic requirements to showcase professional backend development patterns:

- ✅ **Separation of Concerns** - Business logic independent of HTTP layer
- ✅ **Type Safety** - Using dataclasses instead of dictionaries
- ✅ **Exception-Based Error Handling** - Clear, consistent error signaling
- ✅ **Comprehensive Testing** - Unit tests without Flask dependency
- ✅ **Clean Architecture** - Organized, maintainable, scalable code

## 📁 Project Structure

```
book-library-api/
├── app.py              # Flask HTTP layer (thin routes)
├── service.py          # Business logic (testable, reusable)
├── models.py           # Data models (Book dataclass)
├── validators.py       # Input validation logic
├── exceptions.py       # Custom exceptions
├── test_service.py     # Unit tests (30+ test cases)
├── requirements.txt    # Dependencies
└── README.md          # This file
```

### Architecture Layers

```
┌─────────────────────────────┐
│   HTTP Layer (app.py)       │  ← Flask routes, request/response
├─────────────────────────────┤
│   Business (service.py)     │  ← Core logic, rules, workflows
├─────────────────────────────┤
│   Validation (validators.py)│  ← Input validation
├─────────────────────────────┤
│   Models (models.py)        │  ← Type-safe data structures
├─────────────────────────────┤
│   Exceptions (exceptions.py)│  ← Error types
└─────────────────────────────┘
```

## 🚀 Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Server starts at: `http://localhost:5000`

### 4. Run Tests
```bash
python test_service.py
```

## 📡 API Endpoints

### Base URL
```
http://localhost:5000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books` | List all books |
| GET | `/books/:id` | Get specific book |
| POST | `/books` | Create new book |
| PUT | `/books/:id` | Update book |
| DELETE | `/books/:id` | Delete book |
| GET | `/stats` | Collection statistics |

### Example Requests

#### Create a Book
```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "year": 2008
  }'
```

**Response (201):**
```json
{
  "success": true,
  "message": "Book created successfully",
  "data": {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "year": 2008,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### Get All Books
```bash
curl http://localhost:5000/books
```

#### Update a Book
```bash
curl -X PUT http://localhost:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"year": 2023}'
```

#### Delete a Book
```bash
curl -X DELETE http://localhost:5000/books/1
```

## 🏗️ Architecture Details

### Why This Architecture?

This project follows **clean architecture** principles to ensure:
1. **Testability** - Business logic testable without Flask
2. **Reusability** - Service layer works in CLI, GUI, different frameworks
3. **Maintainability** - Clear separation makes code easy to understand
4. **Scalability** - Easy to add features without breaking existing code

### Key Components

#### 1. Models (`models.py`)
Type-safe data structures using Python dataclasses:

```python
@dataclass
class Book:
    title: str
    author: str
    isbn: str
    year: int
    id: Optional[int] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
```

**Benefits:**
- Type safety (IDE autocomplete, type checking)
- No dictionary key errors
- Self-documenting code

#### 2. Validators (`validators.py`)
Centralized validation logic:

```python
class BookValidator:
    @staticmethod
    def validate_year(year: int) -> None:
        """Raises ValidationError if invalid"""
        year_int = int(year)
        if year_int < 1000 or year_int > current_year:
            raise ValidationError("Year out of range")
```

**Benefits:**
- Single source of truth for validation rules
- Reusable across different contexts
- Easy to test

#### 3. Exceptions (`exceptions.py`)
Custom exception types for clear error signaling:

```python
class ValidationError(BookLibraryError):
    """Raised when input validation fails"""
    
class BookNotFoundError(BookLibraryError):
    """Raised when book doesn't exist"""
    
class DuplicateISBNError(BookLibraryError):
    """Raised when ISBN already exists"""
```

**Benefits:**
- Can't be ignored (unlike return tuples)
- Type-safe error handling
- Clear error semantics

#### 4. Service Layer (`service.py`)
Pure business logic, framework-agnostic:

```python
class BookService:
    def create_book(self, data: dict) -> Book:
        """Create book - no Flask knowledge!"""
        BookValidator.validate_book_data(data)
        
        if self._isbn_exists(data['isbn']):
            raise DuplicateISBNError(data['isbn'])
        
        book = Book(...)
        self._books.append(book)
        return book
```

**Benefits:**
- Testable without Flask
- Reusable in any context
- Framework-independent

#### 5. HTTP Layer (`app.py`)
Thin Flask routes that only handle HTTP concerns:

```python
@app.route('/books', methods=['POST'])
def create_book():
    """Thin handler - just HTTP"""
    if not request.is_json:
        return create_error_response("Must be JSON", 400)
    
    try:
        data = request.get_json()
        book = book_service.create_book(data)  # Call service
        return create_success_response(book, 201)
    except ValidationError as e:
        return create_error_response(str(e), 400)
```

**Benefits:**
- Routes stay simple
- Easy to understand
- Business logic stays in service layer

## ✅ Validation Rules

### Required Fields (POST)
- `title` - Non-empty string
- `author` - Non-empty string  
- `isbn` - 10 or 13 digits (hyphens/spaces allowed)
- `year` - Integer between 1000 and current year

### Update Rules (PUT)
- Any combination of fields
- Same validation as POST for provided fields
- ISBN must remain unique

### Business Rules
- No duplicate ISBNs allowed
- Year cannot be in the future
- All text fields trimmed of whitespace

## 🧪 Testing

### Unit Tests
Test business logic directly without Flask:

```bash
python test_service.py
```

**Test Coverage:**
- ✅ Create book (success, validation errors, duplicates)
- ✅ Read books (all, by ID, not found)
- ✅ Update book (partial, full, validation, duplicates)
- ✅ Delete book (success, not found)
- ✅ Statistics calculation

**Example Test:**
```python
def test_create_book_success(self):
    service = BookService()
    book = service.create_book({
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'isbn': '9780132350884',
        'year': 2008
    })
    self.assertEqual(book.title, 'Clean Code')
```

## 🎓 Learning Outcomes

### Week 2 Requirements ✅
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes (200, 201, 400, 404, 500)
- REST architecture
- Flask routing
- JSON handling
- Input validation
- Error handling

### Professional Patterns (Bonus) 🌟
- **Clean Architecture** - Separation of concerns
- **Service Layer Pattern** - Business logic isolation
- **Type Safety** - Using dataclasses
- **Exception Handling** - Consistent error strategy
- **Unit Testing** - Testing without infrastructure
- **Single Responsibility** - Each module does one thing

## 🔧 Configuration

Environment variables (set in terminal or `.env` file):

```bash
PORT=5000           # Server port
DEBUG=True          # Debug mode
FLASK_APP=app.py    # Flask app file
```

## 📊 HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation failed, invalid input |
| 404 | Not Found | Book doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Internal Server Error | Unexpected error |

## 🚀 Next Steps

To extend this project:

1. **Add Database** - Replace in-memory storage with SQLAlchemy
2. **Add Authentication** - JWT or session-based auth
3. **Add Pagination** - Handle large collections
4. **Add Search** - Filter by title, author, year
5. **Add Logging** - Track API usage
6. **Add Docker** - Containerize the app
7. **Add API Docs** - OpenAPI/Swagger documentation

## 💡 Key Takeaways

### Why Separation of Concerns Matters

**Before (typical beginner approach):**
```python
@app.route('/books', methods=['POST'])
def create_book():
    # Validation, business logic, HTTP response all mixed
    # Hard to test, hard to reuse, hard to maintain
```

**After (this project):**
```python
# Service layer (testable, reusable)
class BookService:
    def create_book(self, data: dict) -> Book:
        # Pure business logic
        
# HTTP layer (thin, simple)
@app.route('/books', methods=['POST'])
def create_book():
    # Just handle HTTP
```

### Benefits You Get

1. **Test business logic without Flask** - Fast unit tests
2. **Reuse in different contexts** - CLI, GUI, different API frameworks
3. **Clear error handling** - Exceptions that can't be ignored
4. **Type safety** - Catch errors during development
5. **Easy to extend** - Add features without breaking existing code

## 📝 Common Mistakes Avoided

❌ Mixing business logic with HTTP handling  
✅ Separated into service layer

❌ Using dictionaries for data models  
✅ Using type-safe dataclasses

❌ Returning tuples for errors  
✅ Using exceptions

❌ Validation scattered throughout code  
✅ Centralized in validators module

❌ Can only test via HTTP  
✅ Unit testable business logic

## 🤝 About This Project

This is an educational project for Week 2 of the Backend Engineering Fundamentals course. While it meets all the basic requirements (CRUD API, validation, error handling), it goes further to demonstrate professional development practices that will serve you well as you advance in backend development.

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [REST API Best Practices](https://restfulapi.net/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Unit Testing in Python](https://docs.python.org/3/library/unittest.html)
