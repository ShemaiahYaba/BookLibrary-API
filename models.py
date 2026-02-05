"""
SQLAlchemy ORM Models

This module defines the database models using SQLAlchemy ORM.
Demonstrates:
- One-to-Many relationships (Author -> Books)
- Many-to-Many relationships (Books <-> Categories)
- Proper foreign keys and constraints
- Model methods for serialization
"""

from datetime import datetime
from database import db


# Association table for Many-to-Many relationship between Books and Categories
book_categories = db.Table('book_categories',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Author(db.Model):
    """
    Author model - One author can have many books
    
    Demonstrates:
    - One-to-Many relationship with Book
    - Cascade delete (deleting author deletes their books)
    """
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    bio = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One author has many books
    books = db.relationship('Book', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_books=False):
        """Convert author to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': self.books.count()
        }
        
        if include_books:
            data['books'] = [book.to_dict(include_author=False) for book in self.books]
        
        return data
    
    def __repr__(self):
        return f'<Author {self.name}>'


class Category(db.Model):
    """
    Category model - Books can have multiple categories
    
    Demonstrates:
    - Many-to-Many relationship with Book
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship: Many-to-Many with books
    books = db.relationship('Book', secondary=book_categories, backref=db.backref('categories', lazy='dynamic'))
    
    def to_dict(self, include_books=False):
        """Convert category to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'book_count': len(self.books)
        }
        
        if include_books:
            data['books'] = [book.to_dict(include_categories=False, include_author=False) for book in self.books]
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Book(db.Model):
    """
    Book model - Central entity with relationships to Author and Categories
    
    Demonstrates:
    - Foreign key to Author (Many-to-One)
    - Many-to-Many relationship with Categories
    - Indexes for search optimization
    """
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    
    # Foreign key to Author
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: relationships are defined in Author and Category using backref
    
    def to_dict(self, include_author=True, include_categories=True):
        """Convert book to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'isbn': self.isbn,
            'year': self.year,
            'description': self.description,
            'pages': self.pages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
                'country': self.author.country
            }
        else:
            data['author_id'] = self.author_id
        
        if include_categories:
            data['categories'] = [cat.to_dict(include_books=False) for cat in self.categories]
        
        return data
    
    def __repr__(self):
        return f'<Book {self.title}>'
