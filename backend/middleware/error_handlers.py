"""
Error Handlers for ManimAI Flask Application
Centralized error handling and logging
"""

import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Handle Marshmallow validation errors"""
        logger.warning(f"Validation error: {e.messages}")
        return jsonify({
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """Handle bad request errors"""
        logger.warning(f"Bad request: {request.url} - {e.description}")
        return jsonify({
            'message': 'Bad request',
            'error': e.description
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """Handle unauthorized errors"""
        logger.warning(f"Unauthorized access: {request.url}")
        return jsonify({
            'message': 'Unauthorized access'
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """Handle forbidden errors"""
        logger.warning(f"Forbidden access: {request.url}")
        return jsonify({
            'message': 'Access forbidden'
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle not found errors"""
        logger.warning(f"Resource not found: {request.url}")
        return jsonify({
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle method not allowed errors"""
        logger.warning(f"Method not allowed: {request.method} {request.url}")
        return jsonify({
            'message': 'Method not allowed'
        }), 405
    
    @app.errorhandler(413)
    def handle_payload_too_large(e):
        """Handle payload too large errors"""
        logger.warning(f"Payload too large: {request.url}")
        return jsonify({
            'message': 'File too large'
        }), 413
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(e):
        """Handle rate limit exceeded errors"""
        logger.warning(f"Rate limit exceeded: {request.url}")
        return jsonify({
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {request.url} - {str(e)}")
        return jsonify({
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(502)
    def handle_bad_gateway(e):
        """Handle bad gateway errors"""
        logger.error(f"Bad gateway: {request.url}")
        return jsonify({
            'message': 'Service temporarily unavailable'
        }), 502
    
    @app.errorhandler(503)
    def handle_service_unavailable(e):
        """Handle service unavailable errors"""
        logger.error(f"Service unavailable: {request.url}")
        return jsonify({
            'message': 'Service temporarily unavailable'
        }), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle generic HTTP exceptions"""
        logger.warning(f"HTTP exception: {e.code} - {request.url}")
        return jsonify({
            'message': e.description or 'An error occurred'
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle generic exceptions"""
        logger.error(f"Unhandled exception: {request.url} - {str(e)}", exc_info=True)
        return jsonify({
            'message': 'An unexpected error occurred'
        }), 500