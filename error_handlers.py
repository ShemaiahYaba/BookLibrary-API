"""
Error handlers for the Flask application

Centralized error handling for common HTTP errors.
"""

from utils import create_error_response


def register_error_handlers(app):
    """
    Register error handlers with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return create_error_response("Resource not found", 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return create_error_response("Method not allowed for this endpoint", 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return create_error_response("Internal server error", 500)
