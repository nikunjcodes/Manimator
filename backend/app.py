"""
ManimAI Flask Application
Main application entry point with comprehensive error handling and security
"""

import os
import logging
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from services.database_service import DatabaseService
from services.auth_service import AuthService
from services.gemini_service import GeminiService
from services.manim_service import ManimService
from services.cloudinary_service import CloudinaryService
from services.animation_service import AnimationService
from routes.auth_routes import auth_bp
from routes.animation_routes import animation_bp
from routes.chat_routes import chat_bp
from middleware.error_handlers import register_error_handlers
from middleware.security import setup_security_headers
from utils.logger import setup_logging

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    cors = CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # Rate limiting (using memory storage)
    limiter = Limiter(
        app=app,
        default_limits=["1000 per hour", "100 per minute"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        key_func=get_remote_address
    )
    
    # Initialize services
    db_service = DatabaseService(mongo_uri=app.config['MONGO_URI'])
    auth_service = AuthService(db_service)
    manim_service = ManimService(db_service=db_service)
    animation_service = AnimationService(db_service=db_service, manim_service=manim_service)
    cloudinary_service = CloudinaryService(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET']
    )
    gemini_service = GeminiService(api_key=app.config['GEMINI_API_KEY'])
    
    # Store services in app context
    app.db_service = db_service
    app.auth_service = auth_service
    app.gemini_service = gemini_service
    app.manim_service = manim_service
    app.cloudinary_service = cloudinary_service
    app.animation_service = animation_service
    
    # JWT configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return auth_service.is_token_revoked(jwt_payload['jti'])
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Authorization token required'}), 401
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(animation_bp, url_prefix='/api/animations')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    register_error_handlers(app)
    
    setup_security_headers(app)
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            db_service.health_check()
            gemini_service.health_check()
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'services': {
                    'database': 'connected',
                    'gemini': 'available',
                    'manim': 'available',
                    'cloudinary': 'available'
                }
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 503
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': 'ManimAI API',
            'version': '1.0.0',
            'description': 'AI-powered mathematical animation generator using Gemini and Manim',
            'endpoints': {
                'auth': '/api/auth',
                'animations': '/api/animations',
                'chat': '/api/chat',
                'health': '/api/health'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )