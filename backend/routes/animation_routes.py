"""
Animation Routes for ManimAI
Handles animation creation, management, and file operations
"""

import logging
import asyncio
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime
import uuid
from functools import wraps

logger = logging.getLogger(__name__)

# Create blueprint
animation_bp = Blueprint('animations', __name__)

# Validation schemas
class CreateAnimationSchema(Schema):
    prompt = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    title = fields.Str(validate=lambda x: len(x.strip()) >= 3)
    description = fields.Str()
    is_public = fields.Bool(missing=False)
    tags = fields.List(fields.Str(), missing=[])

class UpdateAnimationSchema(Schema):
    title = fields.Str(validate=lambda x: len(x.strip()) >= 3)
    description = fields.Str()
    is_public = fields.Bool()
    tags = fields.List(fields.Str())

class RegenerateAnimationSchema(Schema):
    prompt = fields.Str(validate=lambda x: len(x.strip()) >= 10)
    improvement_request = fields.Str()

class GenerateAnimationSchema(Schema):
    prompt = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    quality = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']), missing='medium')

@animation_bp.route('/', methods=['POST'])
@jwt_required()
def create_animation():
    """Create a new animation"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = CreateAnimationSchema()
        data = schema.load(request.json)
        
        # Generate unique animation ID
        animation_id = str(uuid.uuid4())
        
        # Generate Manim code using Gemini
        gemini_service = current_app.gemini_service
        ai_result = gemini_service.generate_manim_code(data['prompt'])
        
        if not ai_result.get('code'):
            return jsonify({'message': 'Failed to generate animation code'}), 500
        
        # Create animation record in database
        animation_data = {
            'user_id': user_id,
            'title': data.get('title') or ai_result.get('title', 'Generated Animation'),
            'prompt': data['prompt'],
            'description': data.get('description') or ai_result.get('description', ''),
            'manim_code': ai_result['code'],
            'status': 'pending',
            'is_public': data['is_public'],
            'tags': data['tags'],
            'ai_metadata': {
                'explanation': ai_result.get('explanation', ''),
                'educational_value': ai_result.get('educational_value', ''),
                'suggestions': ai_result.get('suggestions', [])
            }
        }
        
        db_service = current_app.db_service
        db_animation_id = db_service.create_animation(animation_data)
        
        # Start async animation generation
        asyncio.create_task(
            _generate_animation_async(animation_id, db_animation_id, ai_result['code'])
        )
        
        return jsonify({
            'message': 'Animation creation started',
            'animation_id': db_animation_id,
            'status': 'pending',
            'estimated_time': '2-5 minutes'
        }), 202
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Animation creation error: {e}")
        return jsonify({'message': 'Animation creation failed'}), 500

@animation_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_animations():
    """Get user's animations"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        
        db_service = current_app.db_service
        animations = db_service.get_user_animations(user_id, limit, offset)
        
        # Filter by status if provided
        if status:
            animations = [a for a in animations if a.get('status') == status]
        
        # Format response
        formatted_animations = []
        for animation in animations:
            formatted_animations.append({
                'id': animation['_id'],
                'title': animation['title'],
                'prompt': animation['prompt'],
                'description': animation.get('description', ''),
                'status': animation['status'],
                'is_public': animation.get('is_public', False),
                'tags': animation.get('tags', []),
                'views': animation.get('views', 0),
                'duration': animation.get('duration'),
                'video_url': animation.get('video_url'),
                'thumbnail_url': animation.get('thumbnail_url'),
                'created_at': animation['created_at'].isoformat(),
                'updated_at': animation['updated_at'].isoformat()
            })
        
        return jsonify({
            'animations': formatted_animations,
            'total': len(formatted_animations),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get animations error: {e}")
        return jsonify({'message': 'Failed to get animations'}), 500

@animation_bp.route('/<animation_id>', methods=['GET'])
@jwt_required()
def get_animation(animation_id):
    """Get specific animation"""
    try:
        user_id = get_jwt_identity()
        
        db_service = current_app.db_service
        animation = db_service.get_animation_by_id(animation_id)
        
        if not animation:
            return jsonify({'message': 'Animation not found'}), 404
        
        # Check if user owns the animation or it's public
        if animation['user_id'] != user_id and not animation.get('is_public', False):
            return jsonify({'message': 'Access denied'}), 403
        
        # Increment view count if not owner
        if animation['user_id'] != user_id:
            db_service.increment_animation_views(animation_id)
        
        return jsonify({
            'animation': {
                'id': animation['_id'],
                'title': animation['title'],
                'prompt': animation['prompt'],
                'description': animation.get('description', ''),
                'status': animation['status'],
                'is_public': animation.get('is_public', False),
                'tags': animation.get('tags', []),
                'views': animation.get('views', 0),
                'duration': animation.get('duration'),
                'video_url': animation.get('video_url'),
                'thumbnail_url': animation.get('thumbnail_url'),
                'manim_code': animation.get('manim_code') if animation['user_id'] == user_id else None,
                'ai_metadata': animation.get('ai_metadata', {}),
                'created_at': animation['created_at'].isoformat(),
                'updated_at': animation['updated_at'].isoformat(),
                'error_message': animation.get('error_message')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get animation error: {e}")
        return jsonify({'message': 'Failed to get animation'}), 500

@animation_bp.route('/<animation_id>', methods=['PUT'])
@jwt_required()
def update_animation(animation_id):
    """Update animation metadata"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = UpdateAnimationSchema()
        data = schema.load(request.json)
        
        db_service = current_app.db_service
        animation = db_service.get_animation_by_id(animation_id)
        
        if not animation:
            return jsonify({'message': 'Animation not found'}), 404
        
        if animation['user_id'] != user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Update animation
        success = db_service.update_animation(animation_id, data)
        
        if success:
            return jsonify({'message': 'Animation updated successfully'}), 200
        else:
            return jsonify({'message': 'Animation update failed'}), 500
            
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Update animation error: {e}")
        return jsonify({'message': 'Animation update failed'}), 500

@animation_bp.route('/<animation_id>', methods=['DELETE'])
@jwt_required()
def delete_animation(animation_id):
    """Delete an animation"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        # Validate ownership
        if not validate_animation_ownership(animation_id, user_id):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get animation service from app context
        animation_service = current_app.animation_service
        
        # Delete animation
        success = animation_service.delete_animation(animation_id)
        
        if success:
            return jsonify({
                'message': 'Animation deleted successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to delete animation'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to delete animation: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to delete animation',
            'message': str(e)
        }), 500

@animation_bp.route('/public', methods=['GET'])
def get_public_animations():
    """Get public animations"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        tags = request.args.getlist('tags')
        
        # This would need to be implemented in database service
        # animations = db_service.get_public_animations(limit, offset, tags)
        
        return jsonify({
            'animations': [],
            'total': 0,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get public animations error: {e}")
        return jsonify({'message': 'Failed to get public animations'}), 500

@animation_bp.route('/<animation_id>/download', methods=['GET'])
@jwt_required()
def download_animation(animation_id):
    """Download animation video"""
    try:
        user_id = get_jwt_identity()
        
        db_service = current_app.db_service
        animation = db_service.get_animation_by_id(animation_id)
        
        if not animation:
            return jsonify({'message': 'Animation not found'}), 404
        
        # Check access permissions
        if animation['user_id'] != user_id and not animation.get('is_public', False):
            return jsonify({'message': 'Access denied'}), 403
        
        if animation['status'] != 'completed':
            return jsonify({'message': 'Animation not ready for download'}), 400
        
        # Generate download URL from Cloudinary
        cloudinary_service = current_app.cloudinary_service
        video_public_id = f"animations/{animation_id}/video"
        download_url = cloudinary_service.generate_download_url(video_public_id)
        
        if download_url:
            return jsonify({'download_url': download_url}), 200
        else:
            return jsonify({'message': 'Download URL generation failed'}), 500
            
    except Exception as e:
        logger.error(f"Download animation error: {e}")
        return jsonify({'message': 'Download failed'}), 500

@animation_bp.route('/<animation_id>/regenerate', methods=['POST'])
@jwt_required()
def regenerate_animation(animation_id):
    """Regenerate animation with improvements"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = RegenerateAnimationSchema()
        data = schema.load(request.json)
        
        db_service = current_app.db_service
        animation = db_service.get_animation_by_id(animation_id)
        
        if not animation:
            return jsonify({'message': 'Animation not found'}), 404
        
        if animation['user_id'] != user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Generate improved code
        gemini_service = current_app.gemini_service
        
        if data.get('improvement_request'):
            # Improve existing code
            ai_result = gemini_service.improve_manim_code(
                animation.get('manim_code', ''),
                data['improvement_request']
            )
        else:
            # Generate new code from new prompt
            ai_result = gemini_service.generate_manim_code(data['prompt'])
        
        if not ai_result.get('code'):
            return jsonify({'message': 'Failed to generate improved animation code'}), 500
        
        # Update animation record
        update_data = {
            'manim_code': ai_result['code'],
            'status': 'pending',
            'ai_metadata': {
                'explanation': ai_result.get('explanation', ''),
                'educational_value': ai_result.get('educational_value', ''),
                'suggestions': ai_result.get('suggestions', [])
            }
        }
        
        if data.get('prompt'):
            update_data['prompt'] = data['prompt']
        
        db_service.update_animation(animation_id, update_data)
        
        # Start async regeneration
        asyncio.create_task(
            _generate_animation_async(animation_id, animation_id, ai_result['code'])
        )
        
        return jsonify({
            'message': 'Animation regeneration started',
            'animation_id': animation_id,
            'status': 'pending'
        }), 202
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Regenerate animation error: {e}")
        return jsonify({'message': 'Animation regeneration failed'}), 500

@animation_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_animation_stats():
    """Get animation statistics for user"""
    try:
        user_id = get_jwt_identity()
        
        # This would need to be implemented in database service
        # stats = db_service.get_user_animation_stats(user_id)
        
        stats = {
            'total_animations': 0,
            'completed_animations': 0,
            'pending_animations': 0,
            'failed_animations': 0,
            'total_views': 0,
            'public_animations': 0,
            'total_duration': 0
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Get animation stats error: {e}")
        return jsonify({'message': 'Failed to get animation statistics'}), 500

def validate_animation_ownership(animation_id: str, user_id: str) -> bool:
    """Validate that the user owns the animation"""
    try:
        animation = current_app.animation_service.get_animation(animation_id)
        return animation and str(animation['user_id']) == str(user_id)
    except Exception as e:
        logger.error(f"Error validating animation ownership: {e}")
        return False

@animation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_animation():
    """Generate a new animation based on the prompt"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        # Validate request data
        schema = GenerateAnimationSchema()
        data = schema.load(request.json)
        
        # Get animation service from app context
        animation_service = current_app.animation_service
        
        # Generate animation
        result = animation_service.generate_animation(
            user_id=user_id,
            prompt=data['prompt'],
            quality=data['quality']
        )
        
        return jsonify({
            'message': 'Animation generation started',
            'animation_id': result['animation_id'],
            'status': 'pending'
        }), 202
        
    except ValidationError as e:
        logger.warning(f"Validation error in animation generation: {e.messages}")
        return jsonify({
            'error': 'Validation error',
            'messages': e.messages
        }), 400
    except Exception as e:
        logger.error(f"Animation generation failed: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Animation generation failed',
            'message': str(e)
        }), 500

@animation_bp.route('/status/<animation_id>', methods=['GET'])
@jwt_required()
def get_animation_status(animation_id):
    """Get the status of an animation"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        # Validate ownership
        if not validate_animation_ownership(animation_id, user_id):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get animation service from app context
        animation_service = current_app.animation_service
        
        # Get animation
        animation = animation_service.get_animation(animation_id)
        
        if not animation:
            return jsonify({
                'error': 'Animation not found'
            }), 404
        
        return jsonify({
            'animation_id': animation['_id'],
            'status': animation['status'],
            'video_url': animation.get('video_path'),
            'error': animation.get('error')
        })
        
    except Exception as e:
        logger.error(f"Failed to get animation status: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to get animation status',
            'message': str(e)
        }), 500

@animation_bp.route('/list', methods=['GET'])
@jwt_required()
def list_animations():
    """Get list of user's animations"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401

        # Get query parameters
        limit = request.args.get('limit', default=10, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        # Get animation service from app context
        animation_service = current_app.animation_service
        
        # Get user's animations
        animations = animation_service.get_user_animations(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        
        return jsonify({
            'animations': animations,
            'total': len(animations)
        })
        
    except Exception as e:
        logger.error(f"Failed to list animations: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to list animations',
            'message': str(e)
        }), 500

async def _generate_animation_async(animation_id: str, db_animation_id: str, manim_code: str):
    """Async function to generate animation"""
    try:
        # Update status to processing
        db_service = current_app.db_service
        db_service.update_animation(db_animation_id, {
            'status': 'processing',
            'processing_started_at': datetime.utcnow()
        })
        
        # Execute Manim code
        manim_service = current_app.manim_service
        result = await manim_service.execute_manim_code_async(manim_code, animation_id)
        
        if result['success']:
            # Upload files to Cloudinary
            cloudinary_service = current_app.cloudinary_service
            
            # Upload video
            video_result = cloudinary_service.upload_video(
                result['video_path'],
                animation_id,
                title=f"Animation {animation_id}"
            )
            
            # Upload thumbnail
            thumbnail_result = None
            if result.get('thumbnail_path'):
                thumbnail_result = cloudinary_service.upload_thumbnail(
                    result['thumbnail_path'],
                    animation_id
                )
            
            # Update database with results
            update_data = {
                'status': 'completed',
                'processing_completed_at': datetime.utcnow(),
                'video_url': video_result.get('secure_url') if video_result.get('success') else None,
                'thumbnail_url': thumbnail_result.get('secure_url') if thumbnail_result and thumbnail_result.get('success') else None,
                'file_size': result.get('file_size', 0)
            }
            
            # Extract duration from video metadata if available
            if video_result.get('duration'):
                update_data['duration'] = video_result['duration']
            
            db_service.update_animation(db_animation_id, update_data)
            
            # Clean up local files
            manim_service.cleanup_animation_files(animation_id)
            
            logger.info(f"Animation generated successfully: {animation_id}")
            
        else:
            # Update status to failed
            db_service.update_animation(db_animation_id, {
                'status': 'failed',
                'error_message': result.get('error', 'Unknown error'),
                'processing_completed_at': datetime.utcnow()
            })
            
            logger.error(f"Animation generation failed: {animation_id} - {result.get('error')}")
            
    except Exception as e:
        # Update status to failed
        db_service = current_app.db_service
        db_service.update_animation(db_animation_id, {
            'status': 'failed',
            'error_message': str(e),
            'processing_completed_at': datetime.utcnow()
        })
        
        logger.error(f"Animation generation error: {animation_id} - {e}")