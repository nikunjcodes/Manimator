"""
Cloudinary Service for ManimAI
Handles file upload, storage, and CDN delivery
"""

import logging
import os
from typing import Dict, Optional, Any, List
import cloudinary
import cloudinary.uploader
import cloudinary.api
from pathlib import Path

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service for managing files with Cloudinary"""
    
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """Initialize Cloudinary service"""
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError("Cloudinary credentials are required")
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        self.cloud_name = cloud_name
        logger.info("Cloudinary service initialized successfully")
    
    def upload_video(self, file_path: str, public_id: str = None, folder: str = "animations") -> Dict[str, Any]:
        """Upload video file to Cloudinary"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Generate public_id if not provided
            if not public_id:
                public_id = f"{folder}/{Path(file_path).stem}"
            
            # Upload video
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video",
                public_id=public_id,
                folder=folder,
                overwrite=True,
                notification_url=None,
                eager=[
                    {"quality": "auto", "fetch_format": "auto"},
                    {"quality": "auto:low", "fetch_format": "auto"},
                    {"quality": "auto:good", "fetch_format": "auto"}
                ],
                eager_async=True,
                tags=["manim", "animation", "mathematical"]
            )
            
            logger.info(f"Video uploaded successfully: {result.get('public_id')}")
            
            return {
                'success': True,
                'public_id': result.get('public_id'),
                'url': result.get('secure_url'),
                'format': result.get('format'),
                'duration': result.get('duration'),
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes'),
                'created_at': result.get('created_at'),
                'version': result.get('version'),
                'resource_type': result.get('resource_type')
            }
            
        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_thumbnail(self, file_path: str, public_id: str = None, folder: str = "thumbnails") -> Dict[str, Any]:
        """Upload thumbnail image to Cloudinary"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Generate public_id if not provided
            if not public_id:
                public_id = f"{folder}/{Path(file_path).stem}"
            
            # Upload image with transformations
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="image",
                public_id=public_id,
                folder=folder,
                overwrite=True,
                transformation=[
                    {"quality": "auto", "fetch_format": "auto"},
                    {"width": 800, "height": 450, "crop": "fill"},
                ],
                eager=[
                    {"width": 400, "height": 225, "crop": "fill", "quality": "auto"},
                    {"width": 200, "height": 113, "crop": "fill", "quality": "auto"}
                ],
                tags=["thumbnail", "manim", "animation"]
            )
            
            logger.info(f"Thumbnail uploaded successfully: {result.get('public_id')}")
            
            return {
                'success': True,
                'public_id': result.get('public_id'),
                'url': result.get('secure_url'),
                'format': result.get('format'),
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes'),
                'created_at': result.get('created_at'),
                'version': result.get('version'),
                'resource_type': result.get('resource_type')
            }
            
        except Exception as e:
            logger.error(f"Thumbnail upload failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_video_url(self, public_id: str, transformation: Dict[str, Any] = None) -> str:
        """Get optimized video URL"""
        try:
            if transformation:
                return cloudinary.CloudinaryVideo(public_id).build_url(**transformation)
            else:
                return cloudinary.CloudinaryVideo(public_id).build_url(
                    quality="auto",
                    fetch_format="auto"
                )
        except Exception as e:
            logger.error(f"Error generating video URL: {e}")
            return ""
    
    def get_thumbnail_url(self, public_id: str, width: int = 400, height: int = 225) -> str:
        """Get optimized thumbnail URL"""
        try:
            return cloudinary.CloudinaryImage(public_id).build_url(
                width=width,
                height=height,
                crop="fill",
                quality="auto",
                fetch_format="auto"
            )
        except Exception as e:
            logger.error(f"Error generating thumbnail URL: {e}")
            return ""
    
    def delete_file(self, public_id: str, resource_type: str = "video") -> bool:
        """Delete file from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type
            )
            
            success = result.get('result') == 'ok'
            if success:
                logger.info(f"File deleted successfully: {public_id}")
            else:
                logger.warning(f"File deletion failed: {public_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False
    
    def get_file_info(self, public_id: str, resource_type: str = "video") -> Optional[Dict[str, Any]]:
        """Get file information from Cloudinary"""
        try:
            result = cloudinary.api.resource(
                public_id,
                resource_type=resource_type
            )
            
            return {
                'public_id': result.get('public_id'),
                'format': result.get('format'),
                'version': result.get('version'),
                'resource_type': result.get('resource_type'),
                'type': result.get('type'),
                'created_at': result.get('created_at'),
                'bytes': result.get('bytes'),
                'width': result.get('width'),
                'height': result.get('height'),
                'url': result.get('secure_url'),
                'duration': result.get('duration'),  # For videos
                'tags': result.get('tags', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    def list_files(self, folder: str = None, resource_type: str = "video", max_results: int = 100) -> List[Dict[str, Any]]:
        """List files in Cloudinary"""
        try:
            params = {
                'resource_type': resource_type,
                'type': 'upload',
                'max_results': max_results
            }
            
            if folder:
                params['prefix'] = folder
            
            result = cloudinary.api.resources(**params)
            
            files = []
            for resource in result.get('resources', []):
                files.append({
                    'public_id': resource.get('public_id'),
                    'format': resource.get('format'),
                    'version': resource.get('version'),
                    'created_at': resource.get('created_at'),
                    'bytes': resource.get('bytes'),
                    'url': resource.get('secure_url'),
                    'width': resource.get('width'),
                    'height': resource.get('height'),
                    'duration': resource.get('duration'),
                    'tags': resource.get('tags', [])
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get Cloudinary usage statistics"""
        try:
            result = cloudinary.api.usage()
            
            return {
                'plan': result.get('plan'),
                'last_updated': result.get('last_updated'),
                'objects': {
                    'used': result.get('objects', {}).get('used', 0),
                    'limit': result.get('objects', {}).get('limit', 0)
                },
                'bandwidth': {
                    'used': result.get('bandwidth', {}).get('used', 0),
                    'limit': result.get('bandwidth', {}).get('limit', 0)
                },
                'storage': {
                    'used': result.get('storage', {}).get('used', 0),
                    'limit': result.get('storage', {}).get('limit', 0)
                },
                'requests': {
                    'used': result.get('requests', {}).get('used', 0),
                    'limit': result.get('requests', {}).get('limit', 0)
                },
                'transformations': {
                    'used': result.get('transformations', {}).get('used', 0),
                    'limit': result.get('transformations', {}).get('limit', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}
    
    def create_video_playlist(self, video_ids: List[str], playlist_name: str) -> Dict[str, Any]:
        """Create a video playlist"""
        try:
            # This is a custom implementation for creating playlists
            # Cloudinary doesn't have built-in playlist functionality
            # You might want to store playlist information in your database
            
            playlist_data = {
                'name': playlist_name,
                'videos': video_ids,
                'created_at': cloudinary.utils.now(),
                'video_count': len(video_ids)
            }
            
            return {
                'success': True,
                'playlist': playlist_data
            }
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_download_url(self, public_id: str, resource_type: str = "video") -> str:
        """Generate a download URL for a file"""
        try:
            if resource_type == "video":
                return cloudinary.CloudinaryVideo(public_id).build_url(
                    flags="attachment",
                    resource_type="video"
                )
            else:
                return cloudinary.CloudinaryImage(public_id).build_url(
                    flags="attachment",
                    resource_type="image"
                )
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            return ""
    
    def optimize_video_for_web(self, public_id: str) -> Dict[str, str]:
        """Get optimized video URLs for different use cases"""
        try:
            return {
                'auto_quality': cloudinary.CloudinaryVideo(public_id).build_url(
                    quality="auto",
                    fetch_format="auto"
                ),
                'low_quality': cloudinary.CloudinaryVideo(public_id).build_url(
                    quality="auto:low",
                    fetch_format="auto"
                ),
                'good_quality': cloudinary.CloudinaryVideo(public_id).build_url(
                    quality="auto:good",
                    fetch_format="auto"
                ),
                'mobile_optimized': cloudinary.CloudinaryVideo(public_id).build_url(
                    quality="auto:low",
                    width=640,
                    height=360,
                    crop="scale",
                    fetch_format="auto"
                ),
                'preview': cloudinary.CloudinaryVideo(public_id).build_url(
                    start_offset="0",
                    end_offset="10",
                    quality="auto:low",
                    fetch_format="auto"
                )
            }
        except Exception as e:
            logger.error(f"Error optimizing video URLs: {e}")
            return {}