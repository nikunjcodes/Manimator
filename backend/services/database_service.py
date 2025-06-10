"""
Database service for MongoDB operations
Handles all database interactions with proper error handling and connection management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

class DatabaseService:
    """MongoDB database service with connection pooling and error handling"""
    
    def __init__(self, mongo_uri: str, db_name: str = "manimai"):
        """Initialize database connection"""
        try:
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                maxPoolSize=50,
                minPoolSize=5
            )
            self.db = self.client[db_name]
            self._create_indexes()
            logger.info("Database connection established successfully")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Users collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("username", unique=True)
            
            # Animations collection indexes
            self.db.animations.create_index("user_id")
            self.db.animations.create_index("created_at")
            self.db.animations.create_index([("tags", ASCENDING)])
            
            # Chat history indexes
            self.db.chat_history.create_index("user_id")
            self.db.chat_history.create_index("animation_id")
            self.db.chat_history.create_index("created_at")
            
            # Token indexes
            self.db.tokens.create_index("jti", unique=True)
            self.db.tokens.create_index("expires_at", expireAfterSeconds=0)  # TTL index
            self.db.revoked_tokens.create_index("jti", unique=True)
            self.db.revoked_tokens.create_index("revoked_at", expireAfterSeconds=0)  # TTL index
            
            # API keys indexes
            self.db.api_keys.create_index("user_id")
            self.db.api_keys.create_index("key", unique=True)
            self.db.api_keys.create_index("is_active")
            
            # Usage tracking indexes
            self.db.usage.create_index([("user_id", ASCENDING), ("date", ASCENDING)], unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
    
    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            user_data['is_active'] = True
            user_data['subscription'] = 'free'
            
            result = self.db.users.insert_one(user_data)
            logger.info(f"User created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("User with this email already exists")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = self.db.users.find_one({"email": email, "is_active": True})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user = self.db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            update_data['updated_at'] = datetime.utcnow()
            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    # Animation operations
    def create_animation(self, animation_data: Dict[str, Any]) -> str:
        """Create a new animation record"""
        try:
            animation_data['created_at'] = datetime.utcnow()
            animation_data['updated_at'] = datetime.utcnow()
            animation_data['views'] = 0
            animation_data['is_public'] = False
            animation_data['tags'] = animation_data.get('tags', [])
            
            result = self.db.animations.insert_one(animation_data)
            logger.info(f"Animation created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create animation: {e}")
            raise
    
    def get_animation_by_id(self, animation_id: str) -> Optional[Dict[str, Any]]:
        """Get animation by ID"""
        try:
            if not ObjectId.is_valid(animation_id):
                return None
            
            animation = self.db.animations.find_one({"_id": ObjectId(animation_id)})
            if animation:
                animation['_id'] = str(animation['_id'])
            return animation
        except Exception as e:
            logger.error(f"Failed to get animation by ID: {e}")
            return None
    
    def get_user_animations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get animations for a specific user"""
        try:
            if not ObjectId.is_valid(user_id):
                return []
            
            cursor = self.db.animations.find(
                {"user_id": user_id}
            ).sort("created_at", DESCENDING).skip(offset).limit(limit)
            
            animations = []
            for animation in cursor:
                animation['_id'] = str(animation['_id'])
                animations.append(animation)
            
            return animations
        except Exception as e:
            logger.error(f"Failed to get user animations: {e}")
            return []
    
    def update_animation(self, animation_id: str, update_data: Dict[str, Any]) -> bool:
        """Update animation data"""
        try:
            if not ObjectId.is_valid(animation_id):
                return False
            
            update_data['updated_at'] = datetime.utcnow()
            result = self.db.animations.update_one(
                {"_id": ObjectId(animation_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update animation: {e}")
            return False
    
    def increment_animation_views(self, animation_id: str) -> bool:
        """Increment animation view count"""
        try:
            if not ObjectId.is_valid(animation_id):
                return False
            
            result = self.db.animations.update_one(
                {"_id": ObjectId(animation_id)},
                {"$inc": {"views": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to increment animation views: {e}")
            return False
    
    # Chat history operations
    def save_chat_message(self, chat_data: Dict[str, Any]) -> str:
        """Save chat message"""
        try:
            chat_data['created_at'] = datetime.utcnow()
            result = self.db.chat_history.insert_one(chat_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save chat message: {e}")
            raise
    
    def get_chat_history(self, user_id: str, animation_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for user or specific animation"""
        try:
            if not ObjectId.is_valid(user_id):
                return []
            
            query = {"user_id": user_id}
            if animation_id and ObjectId.is_valid(animation_id):
                query["animation_id"] = animation_id
            
            cursor = self.db.chat_history.find(query).sort("created_at", ASCENDING).limit(limit)
            
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return []
    
    # Usage tracking
    def track_usage(self, user_id: str, usage_data: Dict[str, Any]) -> bool:
        """Track user usage for the day"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            today = datetime.utcnow().date()
            
            result = self.db.usage.update_one(
                {"user_id": user_id, "date": today},
                {
                    "$inc": {
                        "animations_generated": usage_data.get("animations_generated", 0),
                        "processing_time_minutes": usage_data.get("processing_time_minutes", 0),
                        "storage_used_mb": usage_data.get("storage_used_mb", 0)
                    },
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            return False
    
    def get_user_usage(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user usage statistics"""
        try:
            if not ObjectId.is_valid(user_id):
                return []
            
            start_date = datetime.utcnow().date() - timedelta(days=days)
            
            cursor = self.db.usage.find(
                {"user_id": user_id, "date": {"$gte": start_date}}
            ).sort("date", DESCENDING)
            
            usage_data = []
            for usage in cursor:
                usage['_id'] = str(usage['_id'])
                usage_data.append(usage)
            
            return usage_data
        except Exception as e:
            logger.error(f"Failed to get user usage: {e}")
            return []
    
    # Token blacklist operations
    def revoke_token(self, jti: str) -> bool:
        """Revoke a token by its JTI"""
        try:
            result = self.db.revoked_tokens.update_one(
                {"jti": jti},
                {"$set": {"revoked_at": datetime.utcnow()}},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False

    def store_token(self, jti: str, expires_at: datetime) -> bool:
        """Store a token in the database"""
        try:
            result = self.db.tokens.insert_one({
                "jti": jti,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            })
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            return False

    def is_token_revoked(self, jti: str) -> bool:
        """Check if a token is revoked"""
        try:
            token = self.db.revoked_tokens.find_one({"jti": jti})
            return token is not None
        except Exception as e:
            logger.error(f"Failed to check token revocation: {e}")
            return True  # Assume revoked on error for security
    
    def close_connection(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")