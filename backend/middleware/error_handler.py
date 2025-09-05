import logging
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        logger.warning(f"Unauthorized access attempt: {error}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        logger.warning(f"Forbidden access attempt: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        logger.info(f"Resource not found: {error}")
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        logger.warning(f"Method not allowed: {error}")
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        logger.critical(f"Unhandled exception: {error}", exc_info=True)
        # In development mode, return more details
        if app.config['DEBUG']:
            return jsonify({
                'error': 'Server error',
                'message': str(error),
                'type': error.__class__.__name__
            }), 500
        # In production, return a generic message
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    # Custom validation error handler
    class ValidationError(Exception):
        """Custom exception for validation errors"""
        def __init__(self, message, errors=None):
            super().__init__(message)
            self.errors = errors or {}
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning(f"Validation error: {error}")
        return jsonify({
            'error': 'Validation error',
            'message': str(error),
            'errors': error.errors
        }), 400
    
    # Expose the ValidationError class to the app
    app.ValidationError = ValidationError