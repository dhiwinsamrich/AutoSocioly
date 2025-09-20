"""
Instagram Poster

Handles posting content to Instagram platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class InstagramPoster(BasePoster):
    """Instagram-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize Instagram poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("instagram")
        self.getlate_service = getlate_service
        self.max_caption_length = 2200
        self.allowed_media_types = ['image/jpeg', 'image/png', 'image/jpg']
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            content: Caption text for the post
            media_urls: List of media URLs (images/videos)
            **kwargs: Additional parameters (location, tags, etc.)
            
        Returns:
            Posting result
        """
        try:
            self.log_post_attempt(content, len(media_urls) if media_urls else 0)
            
            # Validate content
            validation_result = self.validate_content(content, media_urls)
            if not validation_result["valid"]:
                return self.format_response(
                    success=False,
                    message="Content validation failed",
                    error=validation_result["error"]
                )
            
            # Ensure media URLs are provided for Instagram
            if not media_urls or len(media_urls) == 0:
                return self.format_response(
                    success=False,
                    message="Instagram requires at least one media file",
                    error="Media URLs are required for Instagram posts"
                )
            
            # Post to Instagram using GetLate service
            self.logger.info(f"Posting to Instagram with content length: {len(content)}")
            self.logger.info(f"Media URLs: {media_urls}")
            
            result = await asyncio.to_thread(
                self.getlate_service.post_to_instagram,
                content,
                media_urls
            )
            
            self.logger.info(f"Instagram posting result: {result}")
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, content)
                return self.format_response(
                    success=True,
                    message="Successfully posted to Instagram",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to post to Instagram",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while posting to Instagram: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while posting",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get Instagram account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call Instagram's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "instagram",
                "account_id": "instagram_account",
                "status": "active",
                "followers": 0,  # Would be populated from API
                "following": 0,  # Would be populated from API
                "posts_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Instagram account info: {str(e)}")
            return {
                "platform": "instagram",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate content for Instagram-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Media URLs to validate
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check caption length
        if len(content) > self.max_caption_length:
            errors.append(f"Caption exceeds maximum length of {self.max_caption_length} characters")
        
        # Check media requirements
        if not media_urls or len(media_urls) == 0:
            errors.append("Instagram requires at least one media file")
        elif len(media_urls) > 10:
            errors.append("Instagram allows maximum 10 media files per post")
        
        # Validate media URLs
        if media_urls:
            for url in media_urls:
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid media URL: {url}")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": []
        }
    
    def format_instagram_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for Instagram
        
        Args:
            content: Raw content
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        # Add hashtags if provided
        hashtags = kwargs.get('hashtags', [])
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            content = f"{content}\n\n{hashtag_string}"
        
        # Add location tag if provided
        location = kwargs.get('location')
        if location:
            content = f"{content}\n📍 {location}"
        
        return content