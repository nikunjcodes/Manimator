"""
Authentication service for user management and JWT operations
Handles user registration, login, password hashing, and token management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import bcrypt
import jwt
from flask import current_app
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service with JWT token management"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=current_app.config.get('BCRYPT_LOG_ROUNDS', 12))
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_tokens(self, user_id: str, email: str) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        try:
            # Access token payload
            access_payload = {
                'user_id': user_id,
                'email': email,
                'type': 'access',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            }
            
            # Refresh token payload
            refresh_payload = {
                'user_id': user_id,
                'email': email,
                'type': 'refresh',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
            }
            
            access_token = jwt.encode(
                access_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            refresh_token = jwt.encode(
                refresh_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check if token is revoked
            if self.is_token_revoked(payload.get('jti')):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def register_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user data
            user_data = {
                'email': email.lower().strip(),
                'password': hashed_password,
                'name': name.strip(),
                'subscription': 'free',
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Save user to database
            user_id = self.db.create_user(user_data)
            
            # Generate tokens
            tokens = self.generate_tokens(user_id, email)
            
            # Return user data and tokens
            return {
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'subscription': 'free'
                },
                'tokens': tokens
            }
        except ValueError as e:
            logger.warning(f"Registration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Get user from database
            user = self.db.get_user_by_email(email.lower().strip())
            if not user:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, user['password']):
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user.get('is_active', True):
                raise ValueError("Account is deactivated")
            
            # Generate tokens
            tokens = self.generate_tokens(user['_id'], user['email'])
            
            # Update last login
            self.db.update_user(user['_id'], {'last_login': datetime.utcnow()})
            
            return {
                'user': {
                    'id': user['_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'subscription': user.get('subscription', 'free')
                },
                'tokens': tokens
            }
        except ValueError as e:
            logger.warning(f"Login validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"User login failed: {e}")
            raise
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access token using refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get('type') != 'refresh':
                raise ValueError("Invalid refresh token")
            
            # Generate new access token
            tokens = self.generate_tokens(payload['user_id'], payload['email'])
            return {'access_token': tokens['access_token']}
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    def revoke_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return False
            
            expires_at = datetime.fromtimestamp(payload['exp'])
            return self.db.revoke_token(payload.get('jti'), expires_at)
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def is_token_revoked(self, jti: str) -> bool:
        """Check if token is revoked"""
        if not jti:
            return False
        return self.db.is_token_revoked(jti)
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user data from token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            return self.db.get_user_by_id(payload['user_id'])
        except Exception as e:
            logger.error(f"Failed to get user by token: {e}")
            return None
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.db.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Verify old password
            if not self.verify_password(old_password, user['password']):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_hashed_password = self.hash_password(new_password)
            
            # Update password in database
            return self.db.update_user(user_id, {
                'password': new_hashed_password,
                'updated_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            raise
    
    def reset_password_request(self, email: str) -> str:
        """Generate password reset token"""
        try:
            user = self.db.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists
                return "reset_token_placeholder"
            
            # Generate reset token
            reset_payload = {
                'user_id': user['_id'],
                'email': user['email'],
                'type': 'password_reset',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
            }
            
            reset_token = jwt.encode(
                reset_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            # Store reset token in database
            self.db.update_user(user['_id'], {
                'password_reset_token': reset_token,
                'password_reset_expires': datetime.utcnow() + timedelta(hours=1)
            })
            
            return reset_token
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            raise
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            payload = self.verify_token(reset_token)
            if not payload or payload.get('type') != 'password_reset':
                raise ValueError("Invalid or expired reset token")
            
            # Hash new password
            hashed_password = self.hash_password(new_password)
            
            # Update password and clear reset token
            return self.db.update_user(payload['user_id'], {
                'password': hashed_password,
                'password_reset_token': None,
                'password_reset_expires': None,
                'updated_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise
