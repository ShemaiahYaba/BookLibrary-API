"""
RESTful Book Library API - Refactored Version
Week 2 Project - Backend Engineering Fundamentals

This refactored version demonstrates:
- Separation of concerns (business logic vs HTTP handling)
- Clean architecture (models, services, validators, exceptions)
- Consistent error handling strategy
- Type-safe data models
- Testable business logic
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

from service import BookService
from exceptions import (
    BookNotFoundError,
    ValidationError,
    DuplicateISBNError,
    InvalidDataFormatError
)

# Initialize Flask application
app = Flask(__name__)

# Initialize the service layer
# This is our business logic - completely independent of Flask
book_service = BookService()


def create_success_response(data=None, message=None, status_code=200):
    """
    Create a standardized success response
    
    This helper keeps response formatting consistent and
    separates the concern of "what to return" from "how to format it"
    """
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        if isinstance(data, list):
            response['count'] = len(data)
            response['data'] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
        else:
            response['data'] = data.to_dict() if hasattr(data, 'to_dict') else data
    
    return jsonify(response), status_code


def create_error_response(error, status_code=400):
    """
    Create a standardized error response
    
    Centralizes error formatting so business logic doesn't need to know
    about HTTP response structure
    """
    return jsonify({
        'success': False,
        'error': str(error)
    }), status_code


# ==================== ROUTE HANDLERS ====================
# These are THIN - they only handle HTTP concerns:
# - Extract data from requests
# - Call service methods
# - Convert results/exceptions to HTTP responses
# - NO business logic here!


@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        'message': 'Book Library API (Refactored)',
        'version': '2.0',
        'endpoints': {
            'GET /books': 'List all books',
            'GET /books/:id': 'Get a specific book',
            'POST /books': 'Create a new book',
            'PUT /books/:id': 'Update a book',
            'DELETE /books/:id': 'Delete a book',
            'GET /stats': 'Get collection statistics'
        }
    }), 200


@app.route('/books', methods=['GET'])
def get_books():
    """
    Get all books
    
    This handler:
    1. Calls service method
    2. Formats response
    That's it - no business logic!
    """
    try:
        books = book_service.get_all_books()
        return create_success_response(data=books)
    except Exception as e:
        # Unexpected errors
        return create_error_response(str(e), 500)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get a specific book by ID
    
    Notice how clean this is - the route handler just:
    1. Extracts the book_id (Flask does this)
    2. Calls service
    3. Handles the two possible outcomes (success or not found)
    """
    try:
        book = book_service.get_book_by_id(book_id)
        return create_success_response(data=book)
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except Exception as e:
        return create_error_response(str(e), 500)


@app.route('/books', methods=['POST'])
def create_book():
    """
    Create a new book
    
    This handler:
    1. Validates request format (JSON)
    2. Extracts data
    3. Calls service
    4. Converts exceptions to appropriate HTTP responses
    """
    # HTTP-level validation: is it JSON?
    if not request.is_json:
        return create_error_response(
            "Content-Type must be application/json", 
            400
        )
    
    try:
        data = request.get_json()
        book = book_service.create_book(data)
        return create_success_response(
            data=book,
            message="Book created successfully",
            status_code=201
        )
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DuplicateISBNError as e:
        return create_error_response(str(e), 400)
    except Exception as e:
        return create_error_response(str(e), 500)


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Update an existing book
    
    Same pattern: extract, call service, handle exceptions
    """
    if not request.is_json:
        return create_error_response(
            "Content-Type must be application/json",
            400
        )
    
    try:
        data = request.get_json()
        book = book_service.update_book(book_id, data)
        return create_success_response(
            data=book,
            message="Book updated successfully"
        )
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except ValidationError as e:
        return create_error_response(str(e), 400)
    except DuplicateISBNError as e:
        return create_error_response(str(e), 400)
    except Exception as e:
        return create_error_response(str(e), 500)


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book
    
    Again, very clean: call service, handle exceptions
    """
    try:
        book = book_service.delete_book(book_id)
        return create_success_response(
            message=f'Book "{book.title}" deleted successfully'
        )
    except BookNotFoundError as e:
        return create_error_response(str(e), 404)
    except Exception as e:
        return create_error_response(str(e), 500)


@app.route('/stats', methods=['GET'])
def get_statistics():
    """
    Get collection statistics
    
    Example of how easy it is to add new endpoints when
    business logic is separated
    """
    try:
        stats = book_service.get_statistics()
        return create_success_response(data=stats)
    except Exception as e:
        return create_error_response(str(e), 500)


# ==================== ERROR HANDLERS ====================
# Global handlers for HTTP errors


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors (wrong URL)"""
    return create_error_response("Resource not found", 404)


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors (wrong HTTP method)"""
    return create_error_response(
        "Method not allowed for this endpoint",
        405
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors (unexpected server errors)"""
    return create_error_response("Internal server error", 500)


# ==================== APPLICATION STARTUP ====================


if __name__ == '__main__':
    # Configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    
    print(f"Starting Book Library API (Refactored) on port {port}")
    print("\nArchitecture:")
    print("  📁 models.py      - Data models (Book dataclass)")
    print("  📁 validators.py  - Validation logic")
    print("  📁 exceptions.py  - Custom exceptions")
    print("  📁 service.py     - Business logic")
    print("  📁 app.py         - HTTP/Flask layer (this file)")
    print("\nBenefits:")
    print("  ✅ Testable business logic (no Flask needed)")
    print("  ✅ Reusable in different contexts (API, CLI, GUI)")
    print("  ✅ Clear separation of concerns")
    print("  ✅ Type-safe data models")
    print("  ✅ Consistent error handling\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
