"""
Manim Service for ManimAI
Handles Manim code execution and video generation
"""

import os
import subprocess
import tempfile
import logging
import shutil
import asyncio
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ManimService:
    """Service for executing Manim code and generating videos"""
    
    def __init__(self, output_dir: str = "manim_output", quality: str = "medium_quality", timeout: int = 300):
        """Initialize Manim service"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.quality = quality
        self.timeout = timeout
        
        # Quality settings mapping
        self.quality_settings = {
            "low_quality": {"flag": "-ql", "resolution": "480p"},
            "medium_quality": {"flag": "-qm", "resolution": "720p"},
            "high_quality": {"flag": "-qh", "resolution": "1080p"},
            "production_quality": {"flag": "-qp", "resolution": "1440p"}
        }
        
        logger.info(f"Manim service initialized with quality: {quality}")
    
    def execute_manim_code(self, code: str, scene_name: str = None, quality: str = None) -> Dict[str, Any]:
        """Execute Manim code and generate video"""
        try:
            # Use provided quality or default
            quality = quality or self.quality
            if quality not in self.quality_settings:
                quality = "medium_quality"
            
            # Generate unique execution ID
            execution_id = str(uuid.uuid4())
            
            # Create temporary directory for this execution
            temp_dir = self.output_dir / execution_id
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # Prepare the code
                prepared_code = self._prepare_code(code, scene_name)
                
                # Write code to temporary file
                code_file = temp_dir / "animation.py"
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(prepared_code)
                
                # Execute Manim
                result = self._run_manim(code_file, quality, temp_dir)
                
                if result['success']:
                    # Find generated video file
                    video_path = self._find_video_file(temp_dir)
                    if video_path:
                        # Move video to final location
                        final_video_path = self.output_dir / f"{execution_id}.mp4"
                        shutil.move(video_path, final_video_path)
                        
                        # Generate thumbnail
                        thumbnail_path = self._generate_thumbnail(final_video_path)
                        
                        result.update({
                            'video_path': str(final_video_path),
                            'thumbnail_path': str(thumbnail_path) if thumbnail_path else None,
                            'execution_id': execution_id,
                            'file_size': final_video_path.stat().st_size,
                            'resolution': self.quality_settings[quality]['resolution']
                        })
                        
                        logger.info(f"Manim execution successful: {execution_id}")
                    else:
                        result['success'] = False
                        result['error'] = "Video file not found after execution"
                
                return result
                
            finally:
                # Clean up temporary directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"Manim execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_id': execution_id if 'execution_id' in locals() else None
            }
    
    async def execute_manim_code_async(self, code: str, scene_name: str = None, quality: str = None) -> Dict[str, Any]:
        """Execute Manim code asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_manim_code, code, scene_name, quality)
    
    def _prepare_code(self, code: str, scene_name: str = None) -> str:
        """Prepare Manim code for execution"""
        try:
            # Extract scene class name if not provided
            if not scene_name:
                scene_name = self._extract_scene_name(code)
            
            # Ensure proper imports
            if 'from manim import *' not in code and 'from manim import' not in code:
                code = "from manim import *\n\n" + code
            
            # Add execution block if not present
            if '__name__ == "__main__"' not in code:
                code += f"\n\nif __name__ == '__main__':\n    scene = {scene_name}()\n    scene.render()"
            
            return code
            
        except Exception as e:
            logger.error(f"Code preparation failed: {e}")
            raise
    
    def _extract_scene_name(self, code: str) -> str:
        """Extract scene class name from code"""
        import re
        
        # Look for class definition that inherits from Scene
        pattern = r'class\s+(\w+)\s*$$[^)]*Scene[^)]*$$:'
        match = re.search(pattern, code)
        
        if match:
            return match.group(1)
        
        # Fallback: look for any class definition
        pattern = r'class\s+(\w+)\s*$$[^)]*$$:'
        match = re.search(pattern, code)
        
        if match:
            return match.group(1)
        
        raise ValueError("No scene class found in code")
    
    def _run_manim(self, code_file: Path, quality: str, output_dir: Path) -> Dict[str, Any]:
        """Run Manim command"""
        try:
            quality_flag = self.quality_settings[quality]['flag']
            
            # Build Manim command
            cmd = [
                'manim',
                quality_flag,
                '--output_file', str(output_dir),
                '--disable_caching',
                '--write_to_movie',
                str(code_file)
            ]
            
            # Execute command
            start_time = datetime.utcnow()
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=output_dir
            )
            end_time = datetime.utcnow()
            
            execution_time = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'stdout': process.stdout,
                    'stderr': process.stderr,
                    'execution_time': execution_time
                }
            else:
                return {
                    'success': False,
                    'error': process.stderr or process.stdout,
                    'stdout': process.stdout,
                    'stderr': process.stderr,
                    'execution_time': execution_time
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Execution timed out after {self.timeout} seconds",
                'execution_time': self.timeout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0
            }
    
    def _find_video_file(self, directory: Path) -> Optional[Path]:
        """Find the generated video file"""
        try:
            # Look for MP4 files
            video_files = list(directory.rglob("*.mp4"))
            
            if video_files:
                # Return the most recently created video file
                return max(video_files, key=lambda f: f.stat().st_mtime)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding video file: {e}")
            return None
    
    def _generate_thumbnail(self, video_path: Path) -> Optional[Path]:
        """Generate thumbnail from video"""
        try:
            thumbnail_path = video_path.with_suffix('.jpg')
            
            # Use ffmpeg to extract thumbnail
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', '00:00:01',  # Extract frame at 1 second
                '-vframes', '1',
                '-y',  # Overwrite output file
                str(thumbnail_path)
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0 and thumbnail_path.exists():
                return thumbnail_path
            else:
                logger.warning(f"Thumbnail generation failed: {process.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            return None
    
    def validate_manim_installation(self) -> Dict[str, Any]:
        """Validate Manim installation"""
        try:
            # Check Manim version
            process = subprocess.run(
                ['manim', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if process.returncode == 0:
                version = process.stdout.strip()
                return {
                    'installed': True,
                    'version': version,
                    'working': True
                }
            else:
                return {
                    'installed': False,
                    'error': process.stderr,
                    'working': False
                }
                
        except FileNotFoundError:
            return {
                'installed': False,
                'error': 'Manim not found in PATH',
                'working': False
            }
        except Exception as e:
            return {
                'installed': False,
                'error': str(e),
                'working': False
            }
    
    def get_supported_qualities(self) -> Dict[str, Dict[str, str]]:
        """Get supported quality settings"""
        return self.quality_settings.copy()
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Clean up old generated files"""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
            cleaned_count = 0
            
            for file_path in self.output_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} old files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a generated file"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': path.suffix,
                'name': path.name
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None