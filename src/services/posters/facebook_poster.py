"""
Facebook Poster

Handles posting content to Facebook platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class FacebookPoster(BasePoster):
    """Facebook-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize Facebook poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("facebook")
        self.getlate_service = getlate_service
        self.max_post_length = 63206  # Facebook's character limit
        self.max_media_per_post = 50  # Facebook allows many photos
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Facebook
        
        Args:
            content: Post text content
            media_urls: Optional list of media URLs
            **kwargs: Additional parameters (privacy, tags, etc.)
            
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
            
            # Format content for Facebook
            formatted_content = self.format_facebook_content(content, **kwargs)
            
            # Post to Facebook using GetLate service
            result = await asyncio.to_thread(
                self.getlate_service.post_to_facebook,
                formatted_content,
                media_urls
            )
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, formatted_content)
                return self.format_response(
                    success=True,
                    message="Successfully posted to Facebook",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to post to Facebook",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while posting to Facebook: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while posting",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get Facebook account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call Facebook's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "facebook",
                "account_id": "facebook_account",
                "status": "active",
                "friends": 0,  # Would be populated from API
                "followers": 0,  # Would be populated from API
                "posts_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Facebook account info: {str(e)}")
            return {
                "platform": "facebook",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate content for Facebook-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Media URLs to validate
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check post length
        if len(content) > self.max_post_length:
            errors.append(f"Post exceeds maximum length of {self.max_post_length} characters")
        
        # Check media count
        if media_urls and len(media_urls) > self.max_media_per_post:
            errors.append(f"Maximum {self.max_media_per_post} media files allowed per post")
        
        # Validate media URLs
        if media_urls:
            for url in media_urls:
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid media URL: {url}")
        
        # Content warnings
        if len(content) < 10:
            warnings.append("Post content is very short, consider adding more context")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings
        }
    
    def format_facebook_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for Facebook
        
        Args:
            content: Raw content
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # Add hashtags if provided (Facebook supports hashtags)
        hashtags = kwargs.get('hashtags', [])
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            formatted = f"{formatted}\n\n{hashtag_string}"
        
        # Add location tag if provided
        location = kwargs.get('location')
        if location:
            formatted = f"{formatted}\n📍 {location}"
        
        # Add feeling/activity if provided
        feeling = kwargs.get('feeling')
        if feeling:
            formatted = f"{formatted}\n😊 Feeling {feeling}"
        
        # Add mention tags if provided
        mentions = kwargs.get('mentions', [])
        if mentions:
            mention_string = ' '.join([f"@{mention}" for mention in mentions])
            formatted = f"{formatted}\n\n{mention_string}"
        
        return formatted.strip()
    
    def create_story(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """
        Create a Facebook story (if supported by API)
        
        Args:
            content: Story text content
            media_url: Media URL for the story
            **kwargs: Additional story parameters
            
        Returns:
            Story creation result
        """
        # This would implement Facebook story creation
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "Facebook story creation not yet implemented",
            "error": "Story creation requires additional API setup"
        }