"""
Security Middleware for ManimAI Flask Application
Handles security headers and CORS configuration
"""

import logging
from flask import request, jsonify

logger = logging.getLogger(__name__)

def setup_security_headers(app):
    """Setup security headers for the Flask application"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "media-src 'self' https:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=()"
        )
        
        # Strict Transport Security (only in production)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    @app.before_request
    def log_request_info():
        """Log request information for security monitoring"""
        # Log suspicious requests
        user_agent = request.headers.get('User-Agent', '')
        
        # Check for common attack patterns
        suspicious_patterns = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
            'burp', 'w3af', 'acunetix', 'nessus'
        ]
        
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            logger.warning(f"Suspicious user agent detected: {user_agent} from {request.remote_addr}")
        
        # Log requests with unusual headers
        if 'X-Forwarded-For' in request.headers:
            forwarded_for = request.headers.get('X-Forwarded-For')
            logger.info(f"Request with X-Forwarded-For: {forwarded_for}")
    
    @app.before_request
    def validate_content_type():
        """Validate content type for POST/PUT requests"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            
            # Allow JSON and form data
            allowed_types = [
                'application/json',
                'application/x-www-form-urlencoded',
                'multipart/form-data'
            ]
            
            if not any(allowed_type in content_type for allowed_type in allowed_types):
                logger.warning(f"Invalid content type: {content_type} from {request.remote_addr}")
                return jsonify({'message': 'Invalid content type'}), 400