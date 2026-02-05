# Book Library API with Database - Week 3 Project

A production-ready RESTful API with PostgreSQL/SQLite database integration, featuring relationships, search, filtering, and pagination.

## 🎯 Week 3 Enhancements

### New Features

✅ **Database Integration** - PostgreSQL/SQLite with SQLAlchemy ORM  
✅ **Relationships** - One-to-Many (Author → Books), Many-to-Many (Books ↔ Categories)  
✅ **Search Functionality** - Search books by title or author name  
✅ **Filtering** - Filter by category, year, or author  
✅ **Pagination** - Efficient handling of large datasets  
✅ **Database Migrations** - Version control for database schema with Alembic  
✅ **Data Seeding** - Sample data script for testing

### Database Schema

```
Authors (1) ─────< Books (Many) >───── Categories (Many)
    │                 │
    │                 │
    ├─ id            ├─ id
    ├─ name          ├─ title
    ├─ bio           ├─ isbn
    ├─ country       ├─ year
    └─ created_at    ├─ author_id (FK)
                     ├─ description
                     ├─ pages
                     └─ created_at
```

## 📁 Project Structure (Modular)

```
book-library-api/
├── app.py                  # Flask application factory (clean & small!)
├── routes/                 # Blueprint modules (organized by resource)
│   ├── __init__.py        # Exports all blueprints
│   ├── books.py           # Book endpoints
│   ├── authors.py         # Author endpoints
│   ├── categories.py      # Category endpoints
│   └── info.py            # Info endpoints (/, /health)
├── database.py            # Database configuration
├── models.py              # SQLAlchemy ORM models
├── service.py             # Business logic layer
├── validators.py          # Input validation
├── exceptions.py          # Custom exceptions
├── utils.py               # Helper functions (response formatting)
├── error_handlers.py      # Centralized error handling
├── seed.py                # Database seeding script
├── test_api.py            # Comprehensive test script
├── requirements.txt       # Dependencies
├── .env.example           # Environment variables template
├── migrations/            # Alembic migration files
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

#### Option A: SQLite (Default - No Setup Needed)

SQLite is used by default. Database file: `library.db`

#### Option B: PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
# Create database
createdb library_db

# Set environment variable
export DATABASE_URL=postgresql://username:password@localhost:5432/library_db
```

### 4. Initialize Database

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Seed Database (Optional)

```bash
python seed.py
```

### 6. Run Application

```bash
python app.py
```

Server starts at: `http://localhost:5000`

## 📡 API Endpoints

### Books

#### List Books (with Search, Filter, Pagination)

```bash
GET /books?page=1&per_page=10&search=clean&category=programming&year=2008
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)
- `search` - Search in title/author name
- `category` - Filter by category name
- `year` - Filter by publication year
- `author_id` - Filter by author ID

**Response:**

```json
{
  "success": true,
  "data": {
    "books": [...],
    "total": 50,
    "page": 1,
    "per_page": 10,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Book by ID

```bash
GET /books/1
```

#### Create Book

```bash
POST /books
Content-Type: application/json

{
  "title": "Clean Code",
  "isbn": "9780132350884",
  "year": 2008,
  "author_id": 1,
  "description": "A handbook of agile software craftsmanship",
  "pages": 464,
  "category_ids": [1, 2]
}
```

#### Update Book

```bash
PUT /books/1
Content-Type: application/json

{
  "year": 2023,
  "category_ids": [1, 3]
}
```

#### Delete Book

```bash
DELETE /books/1
```

### Authors

#### List Authors (with Pagination)

```bash
GET /authors?page=1&per_page=10
```

#### Get Author by ID

```bash
GET /authors/1?include_books=true
```

#### Create Author

```bash
POST /authors
Content-Type: application/json

{
  "name": "Robert C. Martin",
  "bio": "Software engineer and author",
  "country": "USA"
}
```

#### Update Author

```bash
PUT /authors/1
Content-Type: application/json

{
  "bio": "Updated biography"
}
```

#### Delete Author

```bash
DELETE /authors/1
```

_Note: Cannot delete authors with existing books_

### Categories

#### List All Categories

```bash
GET /categories
```

#### Get Category by ID

```bash
GET /categories/1?include_books=true
```

#### Create Category

```bash
POST /categories
Content-Type: application/json

{
  "name": "Programming",
  "description": "Books about software development"
}
```

#### Delete Category

```bash
DELETE /categories/1
```

## 🗄️ Database Concepts Demonstrated

### 1. SQL Basics

- **SELECT** - Retrieving data
- **INSERT** - Creating records
- **UPDATE** - Modifying records
- **DELETE** - Removing records
- **WHERE** - Filtering data
- **ORDER BY** - Sorting results

### 2. JOINs

```python
# INNER JOIN - Get books with their authors
query = Book.query.join(Author)

# LEFT JOIN - Get all books, with or without categories
query = Book.query.outerjoin(Category)
```

### 3. Relationships

**One-to-Many (Author → Books):**

```python
class Author(db.Model):
    books = db.relationship('Book', backref='author')

class Book(db.Model):
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
```

**Many-to-Many (Books ↔ Categories):**

```python
book_categories = db.Table('book_categories',
    db.Column('book_id', db.ForeignKey('books.id')),
    db.Column('category_id', db.ForeignKey('categories.id'))
)
```

### 4. Aggregation

```python
# Count books per author
author.books.count()

# Get statistics
db.session.query(
    func.count(Book.id),
    func.avg(Book.year),
    func.max(Book.pages)
).all()
```

### 5. Database Normalization

**First Normal Form (1NF):**

- Each column contains atomic values
- Each record is unique (primary key)

**Second Normal Form (2NF):**

- In 1NF
- No partial dependencies (all non-key attributes depend on entire primary key)

**Third Normal Form (3NF):**

- In 2NF
- No transitive dependencies (non-key attributes depend only on primary key)

**Our Schema:**

- ✅ Authors table: `id`, `name`, `bio`, `country`
- ✅ Books table: `id`, `title`, `isbn`, `year`, `author_id`
- ✅ Categories table: `id`, `name`, `description`
- ✅ book_categories: Many-to-many association

## 🔧 Database Migrations

### Why Migrations?

- Version control for database schema
- Track changes over time
- Easy rollback if needed
- Team collaboration

### Common Migration Commands

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Add pages column to books"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show migration history
flask db history
```

### Example Migration

```python
def upgrade():
    op.add_column('books', sa.Column('pages', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('books', 'pages')
```

## 🧪 Testing the API

### Using cURL

```bash
# Search for books
curl "http://localhost:5000/books?search=clean&category=programming"

# Create an author
curl -X POST http://localhost:5000/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "Martin Fowler", "country": "UK"}'

# Create a book
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Refactoring",
    "isbn": "9780201485677",
    "year": 1999,
    "author_id": 1,
    "category_ids": [1]
  }'

# Filter books by year
curl "http://localhost:5000/books?year=2008"

# Get paginated results
curl "http://localhost:5000/books?page=2&per_page=5"
```

## 📊 Sample Queries

The seed script creates sample data. Here are some interesting queries:

```bash
# Find all programming books
GET /books?category=programming

# Search for books by Robert Martin
GET /books?search=robert

# Get all books from 2008
GET /books?year=2008

# Get author with all their books
GET /authors/1?include_books=true

# Get category with all its books
GET /categories/1?include_books=true
```

## 🎓 Learning Outcomes

### Week 3 Concepts Mastered

**Database Fundamentals:**

- ✅ Relational database design
- ✅ Primary and foreign keys
- ✅ Database normalization (1NF, 2NF, 3NF)
- ✅ SQL queries (SELECT, INSERT, UPDATE, DELETE)
- ✅ JOINs (INNER, LEFT)
- ✅ WHERE clauses and filtering
- ✅ Aggregation (COUNT, SUM, AVG)

**SQLAlchemy ORM:**

- ✅ Model definition
- ✅ Relationships (One-to-Many, Many-to-Many)
- ✅ Querying with ORM
- ✅ Session management
- ✅ Transaction handling

**Advanced Features:**

- ✅ Search functionality
- ✅ Filtering and pagination
- ✅ Database migrations with Alembic
- ✅ Connection pooling
- ✅ Data seeding

## 🏗️ Architecture Improvements

### Maintained from Week 2:

- ✅ Separation of concerns (layers)
- ✅ Type-safe models (now with SQLAlchemy)
- ✅ Exception-based error handling
- ✅ Input validation
- ✅ Service layer pattern

### New for Week 3:

- ✅ ORM instead of in-memory storage
- ✅ Database transactions
- ✅ Relationship management
- ✅ Query optimization with indexes
- ✅ Migration version control
- ✅ **Modular Blueprint Architecture** - Routes organized by resource
- ✅ **Application Factory Pattern** - Clean app initialization
- ✅ **Centralized Error Handling** - DRY error management
- ✅ **Utility Functions** - Reusable helpers

### Why Blueprints?

**Before (Monolithic app.py):**

- 450+ lines in one file
- Hard to find specific endpoints
- Difficult to test individual resources
- Merge conflicts in team settings

**After (Modular with Blueprints):**

```
app.py (80 lines) - Just wires everything together
├── routes/books.py (130 lines) - Only book logic
├── routes/authors.py (100 lines) - Only author logic
├── routes/categories.py (80 lines) - Only category logic
└── routes/info.py (60 lines) - Only info endpoints
```

**Benefits:**

- 📦 **Organized** - Each resource in its own file
- 🔍 **Easy to find** - Know exactly where to look
- 🧪 **Testable** - Can test blueprints independently
- 👥 **Team-friendly** - Multiple developers can work on different blueprints
- 🔄 **Reusable** - Blueprints can be shared across projects
- 📈 **Scalable** - Easy to add new resources

<!-- ## 🚦 Next Steps

### Week 4 Preview - Authentication & Authorization
- User registration and login
- JWT tokens
- Password hashing
- Protected routes
- Role-based access control

### Further Enhancements
- [ ] Full-text search
- [ ] Advanced filtering (date ranges, multiple categories)
- [ ] Sorting options
- [ ] Book borrowing/lending system
- [ ] Reviews and ratings
- [ ] File uploads (book covers)
- [ ] API documentation with Swagger
- [ ] Caching with Redis -->

## 📝 Common Issues & Solutions

### Issue: Migration Conflicts

```bash
# Delete migrations folder
rm -rf migrations/

# Re-initialize
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Issue: Database Locked (SQLite)

Close all database connections before running migrations.

### Issue: Foreign Key Constraint

Cannot delete an author with existing books. Delete books first or use cascade.

## 🤝 About This Project

Week 3 project for The Engineer Network Basecamp Cohort 2. Builds upon Week 2 by adding:

- Real database persistence
- Relational data modeling
- Advanced querying capabilities
- Production-ready data management

## 📚 Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [Database Normalization](https://www.guru99.com/database-normalization.html)
