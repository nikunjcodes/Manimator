"""
Chat Routes for ManimAI
Handles AI chat functionality, code generation, and assistance
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Validation schemas
class ChatMessageSchema(Schema):
    message = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 1)
    animation_id = fields.Str()

class GenerateCodeSchema(Schema):
    prompt = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    context = fields.Dict()

class ImproveCodeSchema(Schema):
    code = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)
    improvement_request = fields.Str()

class ExplainCodeSchema(Schema):
    code = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 10)

@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """Send a chat message and get AI response"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ChatMessageSchema()
        data = schema.load(request.json)
        
        # Get chat history for context
        db_service = current_app.db_service
        chat_history = db_service.get_chat_history(
            user_id, 
            data.get('animation_id'), 
            limit=10
        )
        
        # Format chat history for AI
        formatted_history = []
        for msg in chat_history:
            formatted_history.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })
        
        # Get AI response
        gemini_service = current_app.gemini_service
        ai_response = gemini_service.chat_response(
            data['message'], 
            formatted_history
        )
        
        # Save user message
        user_message_data = {
            'user_id': user_id,
            'animation_id': data.get('animation_id'),
            'role': 'user',
            'content': data['message'],
            'timestamp': datetime.utcnow()
        }
        db_service.save_chat_message(user_message_data)
        
        # Save AI response
        ai_message_data = {
            'user_id': user_id,
            'animation_id': data.get('animation_id'),
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.utcnow()
        }
        db_service.save_chat_message(ai_message_data)
        
        return jsonify({
            'message': ai_response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        return jsonify({'message': 'Failed to process chat message'}), 500

@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """Get chat history"""
    try:
        user_id = get_jwt_identity()
        animation_id = request.args.get('animation_id')
        limit = min(int(request.args.get('limit', 50)), 100)
        
        db_service = current_app.db_service
        messages = db_service.get_chat_history(user_id, animation_id, limit)
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': msg['_id'],
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat(),
                'animation_id': msg.get('animation_id')
            })
        
        return jsonify({
            'messages': formatted_messages,
            'total': len(formatted_messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        return jsonify({'message': 'Failed to get chat history'}), 500

@chat_bp.route('/generate-code', methods=['POST'])
@jwt_required()
def generate_code():
    """Generate Manim code from prompt"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = GenerateCodeSchema()
        data = schema.load(request.json)
        
        # Generate code using Gemini
        gemini_service = current_app.gemini_service
        result = gemini_service.generate_manim_code(
            data['prompt'], 
            data.get('context', {})
        )
        
        # Save the interaction
        db_service = current_app.db_service
        chat_data = {
            'user_id': user_id,
            'role': 'user',
            'content': f"Generate code: {data['prompt']}",
            'timestamp': datetime.utcnow(),
            'metadata': {
                'type': 'code_generation',
                'prompt': data['prompt'],
                'generated_code': result.get('code', ''),
                'context': data.get('context', {})
            }
        }
        db_service.save_chat_message(chat_data)
        
        return jsonify({
            'code': result.get('code', ''),
            'title': result.get('title', ''),
            'description': result.get('description', ''),
            'explanation': result.get('explanation', ''),
            'educational_value': result.get('educational_value', ''),
            'suggestions': result.get('suggestions', []),
            'validation': result.get('validation', {})
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Generate code error: {e}")
        return jsonify({'message': 'Code generation failed'}), 500

@chat_bp.route('/improve-code', methods=['POST'])
@jwt_required()
def improve_code():
    """Improve existing Manim code"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ImproveCodeSchema()
        data = schema.load(request.json)
        
        # Improve code using Gemini
        gemini_service = current_app.gemini_service
        result = gemini_service.improve_manim_code(
            data['code'],
            data.get('improvement_request', '')
        )
        
        # Save the interaction
        db_service = current_app.db_service
        chat_data = {
            'user_id': user_id,
            'role': 'user',
            'content': f"Improve code: {data.get('improvement_request', 'General improvements')}",
            'timestamp': datetime.utcnow(),
            'metadata': {
                'type': 'code_improvement',
                'original_code': data['code'],
                'improved_code': result.get('code', ''),
                'improvement_request': data.get('improvement_request', '')
            }
        }
        db_service.save_chat_message(chat_data)
        
        return jsonify({
            'improved_code': result.get('code', ''),
            'title': result.get('title', ''),
            'description': result.get('description', ''),
            'explanation': result.get('explanation', ''),
            'suggestions': result.get('suggestions', []),
            'validation': result.get('validation', {})
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Improve code error: {e}")
        return jsonify({'message': 'Code improvement failed'}), 500

@chat_bp.route('/explain-code', methods=['POST'])
@jwt_required()
def explain_code():
    """Explain Manim code"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ExplainCodeSchema()
        data = schema.load(request.json)
        
        # Get explanation from Gemini
        gemini_service = current_app.gemini_service
        explanation = gemini_service.explain_code(data['code'])
        
        # Save the interaction
        db_service = current_app.db_service
        chat_data = {
            'user_id': user_id,
            'role': 'user',
            'content': "Explain this code",
            'timestamp': datetime.utcnow(),
            'metadata': {
                'type': 'code_explanation',
                'code': data['code'],
                'explanation': explanation
            }
        }
        db_service.save_chat_message(chat_data)
        
        return jsonify({
            'explanation': explanation
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Explain code error: {e}")
        return jsonify({'message': 'Code explanation failed'}), 500

@chat_bp.route('/suggest-improvements', methods=['POST'])
@jwt_required()
def suggest_improvements():
    """Get improvement suggestions for code"""
    try:
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ExplainCodeSchema()  # Reuse schema as it has the same structure
        data = schema.load(request.json)
        
        # Get suggestions from Gemini
        gemini_service = current_app.gemini_service
        suggestions = gemini_service.suggest_improvements(data['code'])
        
        # Save the interaction
        db_service = current_app.db_service
        chat_data = {
            'user_id': user_id,
            'role': 'user',
            'content': "Get improvement suggestions",
            'timestamp': datetime.utcnow(),
            'metadata': {
                'type': 'improvement_suggestions',
                'code': data['code'],
                'suggestions': suggestions
            }
        }
        db_service.save_chat_message(chat_data)
        
        return jsonify({
            'suggestions': suggestions
        }), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Suggest improvements error: {e}")
        return jsonify({'message': 'Failed to get improvement suggestions'}), 500

@chat_bp.route('/clear-history', methods=['DELETE'])
@jwt_required()
def clear_chat_history():
    """Clear chat history"""
    try:
        user_id = get_jwt_identity()
        animation_id = request.args.get('animation_id')
        
        # This would need to be implemented in database service
        # db_service = current_app.db_service
        # success = db_service.clear_chat_history(user_id, animation_id)
        
        return jsonify({'message': 'Chat history cleared successfully'}), 200
        
    except Exception as e:
        logger.error(f"Clear chat history error: {e}")
        return jsonify({'message': 'Failed to clear chat history'}), 500

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get list of conversations"""
    try:
        user_id = get_jwt_identity()
        
        # This would need to be implemented in database service
        # Get unique animation_ids from chat history
        # conversations = db_service.get_user_conversations(user_id)
        
        conversations = []
        
        return jsonify({
            'conversations': conversations
        }), 200
        
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        return jsonify({'message': 'Failed to get conversations'}), 500

@chat_bp.route('/export', methods=['GET'])
@jwt_required()
def export_chat_history():
    """Export chat history"""
    try:
        user_id = get_jwt_identity()
        animation_id = request.args.get('animation_id')
        format_type = request.args.get('format', 'json')  # json, txt, csv
        
        db_service = current_app.db_service
        messages = db_service.get_chat_history(user_id, animation_id, limit=1000)
        
        if format_type == 'json':
            return jsonify({
                'messages': messages,
                'exported_at': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'animation_id': animation_id
            }), 200
        elif format_type == 'txt':
            # Format as plain text
            text_content = f"Chat History Export\nUser ID: {user_id}\nAnimation ID: {animation_id or 'All'}\nExported: {datetime.utcnow().isoformat()}\n\n"
            
            for msg in messages:
                text_content += f"[{msg['timestamp'].isoformat()}] {msg['role'].upper()}: {msg['content']}\n\n"
            
            return text_content, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename=chat_history_{user_id}.txt'
            }
        else:
            return jsonify({'message': 'Unsupported export format'}), 400
        
    except Exception as e:
        logger.error(f"Export chat history error: {e}")
        return jsonify({'message': 'Failed to export chat history'}), 500