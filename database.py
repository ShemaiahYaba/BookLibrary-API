"""
Database configuration and setup

This module handles database connection, configuration, and initialization.
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy()
migrate = Migrate()


def get_database_url():
    """
    Get database URL from environment or use SQLite default
    
    Returns:
        Database connection string
    """
    # Check for PostgreSQL connection string
    postgres_url = os.environ.get('DATABASE_URL')
    
    if postgres_url:
        # Fix for Heroku postgres:// -> postgresql://
        if postgres_url.startswith('postgres://'):
            postgres_url = postgres_url.replace('postgres://', 'postgresql://', 1)
        return postgres_url
    
    # Default to SQLite for development
    basedir = os.path.abspath(os.path.dirname(__file__))
    return f'sqlite:///{os.path.join(basedir, "library.db")}'


def init_db(app):
    """
    Initialize database with Flask app
    
    Args:
        app: Flask application instance
    """
    # Set database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQL_ECHO', 'False') == 'True'
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables if they don't exist (for SQLite)
    with app.app_context():
        db.create_all()
