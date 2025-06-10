"""
Animation service for handling animation generation and management
Uses Gemini for code generation and Manim for rendering
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from services.database_service import DatabaseService
from services.manim_service import ManimService

logger = logging.getLogger(__name__)

class AnimationService:
    """Service for animation generation and management"""
    
    def __init__(self, db_service: DatabaseService, manim_service: ManimService):
        """Initialize animation service"""
        self.db = db_service
        self.manim = manim_service
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_animation(self, user_id: str, prompt: str, quality: str = 'medium') -> Dict[str, Any]:
        """Generate a new animation"""
        try:
            # Generate unique ID for the animation
            animation_id = str(uuid.uuid4())
            
            # Create animation record in database
            animation_data = {
                'user_id': user_id,
                'prompt': prompt,
                'quality': quality,
                'status': 'pending',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            db_animation_id = self.db.create_animation(animation_data)
            
            # Generate Manim code using Gemini
            manim_code = self._generate_manim_code(prompt)
            
            # Start animation generation asynchronously
            self.manim.generate_animation_async(animation_id, db_animation_id, manim_code)
            
            return {
                'animation_id': db_animation_id,
                'status': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Animation generation failed: {str(e)}", exc_info=True)
            raise
    
    def _generate_manim_code(self, prompt: str) -> str:
        """Generate Manim code using Gemini"""
        try:
            # Create a prompt for Gemini
            system_prompt = """You are a Manim expert. Generate Python code using Manim to create an animation based on the user's description.
            Follow these guidelines:
            1. Use only the Manim library (from manim import *)
            2. Create a single Scene class that inherits from Scene
            3. Keep the animation simple and focused
            4. Use clear variable names and add comments
            5. Include proper error handling
            6. The animation should be self-contained and runnable
            7. Use appropriate colors and animations
            8. Keep the duration reasonable (5-10 seconds)
            
            Return only the Python code, no explanations or markdown formatting."""
            
            # Generate code using Gemini
            response = self.model.generate_content([
                system_prompt,
                f"Create a Manim animation for: {prompt}"
            ])
            
            # Extract the code from the response
            code = response.text.strip()
            
            # Ensure the code has proper imports and scene class
            if 'from manim import *' not in code:
                code = 'from manim import *\n\n' + code
            
            if 'class' not in code:
                code += '\n\nclass Scene(Scene):\n    def construct(self):\n        pass'
            
            if '__name__ == "__main__"' not in code:
                code += '\n\nif __name__ == "__main__":\n    scene = Scene()\n    scene.render()'
            
            return code
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}", exc_info=True)
            raise
    
    def get_animation(self, animation_id: str) -> Optional[Dict[str, Any]]:
        """Get animation by ID"""
        try:
            return self.db.get_animation(animation_id)
        except Exception as e:
            logger.error(f"Failed to get animation: {str(e)}", exc_info=True)
            raise
    
    def get_user_animations(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """Get user's animations"""
        try:
            return self.db.get_user_animations(user_id, limit, skip)
        except Exception as e:
            logger.error(f"Failed to get user animations: {str(e)}", exc_info=True)
            raise
    
    def delete_animation(self, animation_id: str) -> bool:
        """Delete animation"""
        try:
            # Get animation to check if it exists and get video path
            animation = self.db.get_animation(animation_id)
            if not animation:
                return False
            
            # Delete video file if it exists
            if animation.get('video_path'):
                try:
                    os.remove(animation['video_path'])
                except Exception as e:
                    logger.warning(f"Failed to delete video file: {str(e)}")
            
            # Delete from database
            return self.db.delete_animation(animation_id)
            
        except Exception as e:
            logger.error(f"Failed to delete animation: {str(e)}", exc_info=True)
            raise 