"""
Authentication Routes for ManimAI
Handles user registration, login, logout, and profile management
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, ValidationError

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Validation schemas
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 2)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

class UpdateProfileSchema(Schema):
    name = fields.Str(validate=lambda x: len(x.strip()) >= 2)
    email = fields.Email()

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 8)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Register user
        auth_service = current_app.auth_service
        result = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': result['user']['_id'],
                'email': result['user']['email'],
                'name': result['user']['name'],
                'subscription': result['user']['subscription']
            },
            'access_token': result['access_token']
        }), 201
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'message': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Login user
        auth_service = current_app.auth_service
        result = auth_service.login_user(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': result['user']['_id'],
                'email': result['user']['email'],
                'name': result['user']['name'],
                'subscription': result['user']['subscription']
            },
            'access_token': result['access_token']
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'message': str(e)}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'message': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        refresh_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        auth_service = current_app.auth_service
        result = auth_service.refresh_access_token(refresh_token)
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': result['access_token']
        }), 200
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 401
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'message': 'Token refresh failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        auth_service = current_app.auth_service
        success = auth_service.logout_user(token)
        
        if success:
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'message': 'Logout failed'}), 500
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'message': 'Logout failed'}), 500

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate():
    """Validate token and return user data"""
    try:
        user_id = get_jwt_identity()
        
        auth_service = current_app.auth_service
        user = auth_service.get_user_profile(user_id)
        
        if user:
            return jsonify({
                'valid': True,
                'user': {
                    'id': user['_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'subscription': user['subscription']
                }
            }), 200
        else:
            return jsonify({'valid': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return jsonify({'valid': False, 'message': 'Token validation failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        
        auth_service = current_app.auth_service
        user = auth_service.get_user_profile(user_id)
        
        if user:
            return jsonify({
                'user': {
                    'id': user['_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'subscription': user['subscription'],
                    'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
                    'email_verified': user.get('email_verified', False)
                }
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'message': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = UpdateProfileSchema()
        data = schema.load(request.json)
        
        auth_service = current_app.auth_service
        success = auth_service.update_user_profile(user_id, data)
        
        if success:
            # Get updated user data
            user = auth_service.get_user_profile(user_id)
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user['_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'subscription': user['subscription']
                }
            }), 200
        else:
            return jsonify({'message': 'Profile update failed'}), 500
            
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'message': 'Profile update failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ChangePasswordSchema()
        data = schema.load(request.json)
        
        auth_service = current_app.auth_service
        success = auth_service.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'message': 'Password change failed'}), 500
            
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'message': 'Password change failed'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        # Validate request data
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)
        
        auth_service = current_app.auth_service
        reset_token = auth_service.request_password_reset(data['email'])
        
        # In production, send email with reset token
        # For now, return success message without revealing if email exists
        return jsonify({
            'message': 'If the email exists, a password reset link has been sent'
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({'message': 'Password reset request failed'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
    try:
        # Validate request data
        schema = ResetPasswordSchema()
        data = schema.load(request.json)
        
        auth_service = current_app.auth_service
        success = auth_service.reset_password(
            token=data['token'],
            new_password=data['new_password']
        )
        
        if success:
            return jsonify({'message': 'Password reset successfully'}), 200
        else:
            return jsonify({'message': 'Invalid or expired reset token'}), 400
            
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'message': 'Password reset failed'}), 500