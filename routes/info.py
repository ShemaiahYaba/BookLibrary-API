"""
Info routes - Blueprint for informational endpoints (home, health check)
"""

from flask import Blueprint, jsonify
from database import db

info_bp = Blueprint('info', __name__)


@info_bp.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        'message': 'Book Library API with Database',
        'version': '3.0',
        'database': 'PostgreSQL/SQLite',
        'features': [
            'SQLAlchemy ORM',
            'Database relationships',
            'Search and filtering',
            'Pagination',
            'Multiple entities (Books, Authors, Categories)'
        ],
        'endpoints': {
            'books': {
                'GET /books': 'List books (with search, filter, pagination)',
                'GET /books/:id': 'Get specific book',
                'POST /books': 'Create book',
                'PUT /books/:id': 'Update book',
                'DELETE /books/:id': 'Delete book'
            },
            'authors': {
                'GET /authors': 'List authors (with pagination)',
                'GET /authors/:id': 'Get specific author',
                'POST /authors': 'Create author',
                'PUT /authors/:id': 'Update author',
                'DELETE /authors/:id': 'Delete author'
            },
            'categories': {
                'GET /categories': 'List all categories',
                'GET /categories/:id': 'Get specific category',
                'POST /categories': 'Create category',
                'DELETE /categories/:id': 'Delete category'
            }
        }
    }), 200


@info_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500
