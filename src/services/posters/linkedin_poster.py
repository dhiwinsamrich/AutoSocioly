"""
LinkedIn Poster

Handles posting content to LinkedIn platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class LinkedInPoster(BasePoster):
    """LinkedIn-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize LinkedIn poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("linkedin")
        self.getlate_service = getlate_service
        self.max_post_length = 3000  # LinkedIn's character limit
        self.max_media_per_post = 9  # LinkedIn allows multiple images
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn
        
        Args:
            content: Post text content
            media_urls: Optional list of media URLs
            **kwargs: Additional parameters (visibility, tags, etc.)
            
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
            
            # Format content for LinkedIn
            formatted_content = self.format_linkedin_content(content, **kwargs)
            
            # Post to LinkedIn using GetLate service
            result = await asyncio.to_thread(
                self.getlate_service.post_to_linkedin,
                formatted_content,
                media_urls
            )
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, formatted_content)
                return self.format_response(
                    success=True,
                    message="Successfully posted to LinkedIn",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to post to LinkedIn",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while posting to LinkedIn: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while posting",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get LinkedIn account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call LinkedIn's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "linkedin",
                "account_id": "linkedin_account",
                "status": "active",
                "connections": 0,  # Would be populated from API
                "followers": 0,  # Would be populated from API
                "posts_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting LinkedIn account info: {str(e)}")
            return {
                "platform": "linkedin",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate content for LinkedIn-specific requirements
        
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
        
        # LinkedIn-specific content guidelines
        if len(content) < 50:
            warnings.append("LinkedIn posts perform better with more substantial content")
        
        # Check for overly promotional content
        promotional_keywords = ['buy now', 'click here', 'limited time', 'sale', 'discount']
        content_lower = content.lower()
        promotional_count = sum(1 for keyword in promotional_keywords if keyword in content_lower)
        
        if promotional_count > 2:
            warnings.append("Content may be too promotional for LinkedIn's professional audience")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings
        }
    
    def format_linkedin_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for LinkedIn
        
        Args:
            content: Raw content
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # Add hashtags if provided (LinkedIn supports hashtags)
        hashtags = kwargs.get('hashtags', [])
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            formatted = f"{formatted}\n\n{hashtag_string}"
        
        # Add mention tags if provided
        mentions = kwargs.get('mentions', [])
        if mentions:
            mention_string = ' '.join([f"@{mention}" for mention in mentions])
            formatted = f"{formatted}\n\n{mention_string}"
        
        # Add article link if provided
        article_url = kwargs.get('article_url')
        if article_url:
            formatted = f"{formatted}\n\nRead more: {article_url}"
        
        return formatted.strip()
    
    def create_company_post(self, content: str, company_id: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Create a post on behalf of a company (if supported)
        
        Args:
            content: Post content
            company_id: Company ID to post as
            media_urls: Optional media URLs
            **kwargs: Additional parameters
            
        Returns:
            Post creation result
        """
        # This would implement LinkedIn company page posting
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "LinkedIn company posting not yet implemented",
            "error": "Company posting requires additional API permissions"
        }
    
    def create_article(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Create a LinkedIn article (if supported)
        
        Args:
            title: Article title
            content: Article content
            **kwargs: Article parameters
            
        Returns:
            Article creation result
        """
        # This would implement LinkedIn article creation
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "LinkedIn article creation not yet implemented",
            "error": "Article creation requires additional API setup"
        }