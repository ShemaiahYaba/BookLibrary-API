"""
Utility functions for the API

Contains helper functions for response formatting and other common tasks.
"""

from flask import jsonify


def create_success_response(data=None, message=None, status_code=200):
    """
    Create standardized success response
    
    Args:
        data: Response data (dict, list, or any JSON-serializable object)
        message: Optional success message
        status_code: HTTP status code (default: 200)
        
    Returns:
        Tuple of (JSON response, status code)
    """
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def create_error_response(error, status_code=400):
    """
    Create standardized error response
    
    Args:
        error: Error message (string or exception)
        status_code: HTTP status code (default: 400)
        
    Returns:
        Tuple of (JSON response, status code)
    """
    return jsonify({
        'success': False,
        'error': str(error)
    }), status_code
