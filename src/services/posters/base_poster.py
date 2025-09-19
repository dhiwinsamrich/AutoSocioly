"""
Base Poster Class

Abstract base class for all social media platform posters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ...utils.logger_config import get_logger

class BasePoster(ABC):
    """Abstract base class for social media platform posters"""
    
    def __init__(self, platform_name: str):
        """
        Initialize the poster
        
        Args:
            platform_name: Name of the social media platform
        """
        self.platform_name = platform_name
        self.logger = get_logger(f'poster.{platform_name}')
    
    @abstractmethod
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to the platform
        
        Args:
            content: Text content to post
            media_urls: Optional list of media URLs (images/videos)
            **kwargs: Platform-specific parameters
            
        Returns:
            Posting result with status and metadata
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information for the platform
        
        Returns:
            Account information and status
        """
        pass
    
    @abstractmethod
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate content for platform-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Optional media URLs
            
        Returns:
            Validation result with any issues found
        """
        pass
    
    def format_response(self, success: bool, message: str, post_id: Optional[str] = None, 
                       error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format a standardized response
        
        Args:
            success: Whether the operation was successful
            message: Success/error message
            post_id: Platform post ID if successful
            error: Error details if failed
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        return {
            "success": success,
            "platform": self.platform_name,
            "message": message,
            "post_id": post_id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
    
    def log_post_attempt(self, content: str, media_count: int = 0):
        """Log posting attempt"""
        self.logger.info(f"Attempting to post to {self.platform_name} - Content length: {len(content)}, Media: {media_count}")
    
    def log_post_success(self, post_id: str, content_preview: str = ""):
        """Log successful post"""
        preview = content_preview[:50] + "..." if len(content_preview) > 50 else content_preview
        self.logger.info(f"Successfully posted to {self.platform_name} - Post ID: {post_id} - Preview: {preview}")
    
    def log_post_failure(self, error: str):
        """Log failed post"""
        self.logger.error(f"Failed to post to {self.platform_name} - Error: {error}")

class PosterFactory:
    """Factory class for creating platform-specific posters"""
    
    _posters = {}
    
    @classmethod
    def register_poster(cls, platform: str, poster_class):
        """Register a poster class"""
        cls._posters[platform.lower()] = poster_class
    
    @classmethod
    def create_poster(cls, platform: str, *args, **kwargs) -> BasePoster:
        """
        Create a poster instance for the specified platform
        
        Args:
            platform: Platform name
            *args: Arguments to pass to poster constructor
            **kwargs: Keyword arguments to pass to poster constructor
            
        Returns:
            Platform-specific poster instance
        """
        platform_lower = platform.lower()
        if platform_lower not in cls._posters:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return cls._posters[platform_lower](*args, **kwargs)
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms"""
        return list(cls._posters.keys())