"""
Book Library API with Database Integration
Week 3 Project - Backend Engineering Fundamentals (Modular Version)

Clean, modular architecture using Flask Blueprints:
- routes/ - Organized API endpoints by resource
- utils.py - Helper functions
- error_handlers.py - Centralized error handling
- database.py - Database configuration
- models.py - ORM models
- service.py - Business logic
- validators.py - Input validation
- exceptions.py - Custom exceptions
"""

from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database configuration
from database import init_db

# Import blueprints
from routes import books_bp, authors_bp, categories_bp, info_bp

# Import error handlers
from error_handlers import register_error_handlers


def create_app():
    """
    Application factory pattern
    
    Creates and configures the Flask application with all blueprints
    and error handlers registered.
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(info_bp)        # Root routes (/, /health)
    app.register_blueprint(books_bp)       # /books/*
    app.register_blueprint(authors_bp)     # /authors/*
    app.register_blueprint(categories_bp)  # /categories/*
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def print_startup_info(app):
    """Print startup information"""
    print("\n" + "="*70)
    print("🚀 Book Library API with Database (Week 3 - Modular)")
    print("="*70)
    print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🌐 Server: http://localhost:{os.environ.get('PORT', 5000)}")
    print(f"🔧 Debug Mode: {os.environ.get('DEBUG', 'True') == 'True'}")
    print("\n📁 Modular Structure:")
    print("  • routes/books.py - Book endpoints")
    print("  • routes/authors.py - Author endpoints")
    print("  • routes/categories.py - Category endpoints")
    print("  • routes/info.py - Info endpoints")
    print("  • utils.py - Helper functions")
    print("  • error_handlers.py - Error handling")
    print("\n✨ Features:")
    print("  • SQLAlchemy ORM")
    print("  • One-to-Many relationships (Author → Books)")
    print("  • Many-to-Many relationships (Books ↔ Categories)")
    print("  • Search and filtering")
    print("  • Pagination")
    print("  • Database migrations with Alembic")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Create application
    app = create_app()
    
    # Print startup information
    print_startup_info(app)
    
    # Run application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
