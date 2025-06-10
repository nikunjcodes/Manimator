"""
Manim service for generating animations
Handles the actual rendering of Manim animations
"""

import logging
import os
import asyncio
import subprocess
from typing import Dict, Any
from services.database_service import DatabaseService
from datetime import datetime

logger = logging.getLogger(__name__)

class ManimService:
    """Service for generating Manim animations"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.output_dir = os.getenv('MANIM_OUTPUT_DIR', 'animations')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_animation_async(self, animation_id: str, db_animation_id: str, code: str) -> None:
        """Start animation generation asynchronously"""
        asyncio.create_task(self._generate_animation_async(animation_id, db_animation_id, code))
    
    async def _generate_animation_async(self, animation_id: str, db_animation_id: str, code: str) -> None:
        """Generate animation asynchronously"""
        try:
            # Create temporary Python file
            temp_file = os.path.join(self.output_dir, f"{animation_id}.py")
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Update status to generating
            self.db.update_animation(db_animation_id, {'status': 'generating'})
            
            # Run Manim command
            output_file = os.path.join(self.output_dir, animation_id)
            command = [
                'manim',
                '-qm',  # Medium quality
                '-o', animation_id,  # Output filename
                temp_file,  # Input file
                'Scene'  # Scene class name
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Animation generated successfully
                video_path = f"{output_file}.mp4"
                if os.path.exists(video_path):
                    # Update database with success
                    self.db.update_animation(db_animation_id, {
                        'status': 'completed',
                        'video_path': video_path,
                        'updated_at': datetime.utcnow()
                    })
                    logger.info(f"Animation generated successfully: {animation_id}")
                else:
                    raise FileNotFoundError(f"Video file not found: {video_path}")
            else:
                # Animation generation failed
                error_msg = stderr.decode().strip()
                self.db.update_animation(db_animation_id, {
                    'status': 'error',
                    'error': error_msg,
                    'updated_at': datetime.utcnow()
                })
                logger.error(f"Animation generation failed: {error_msg}")
                raise Exception(f"Manim generation failed: {error_msg}")
            
        except Exception as e:
            logger.error(f"Animation generation failed: {str(e)}", exc_info=True)
            # Update database with error
            self.db.update_animation(db_animation_id, {
                'status': 'error',
                'error': str(e),
                'updated_at': datetime.utcnow()
            })
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)