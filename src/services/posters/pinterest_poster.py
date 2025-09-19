"""
Pinterest Poster

Handles posting content to Pinterest platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class PinterestPoster(BasePoster):
    """Pinterest-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize Pinterest poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("pinterest")
        self.getlate_service = getlate_service
        self.max_description_length = 500
        self.max_title_length = 100
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Pinterest (create a Pin)
        
        Args:
            content: Pin description text
            media_urls: List of media URLs (required for Pinterest)
            **kwargs: Additional parameters (board_id, title, link, etc.)
            
        Returns:
            Posting result
        """
        try:
            # Extract required parameters
            board_id = kwargs.get('board_id')
            title = kwargs.get('title', content[:100])  # Use first 100 chars as title if not provided
            link = kwargs.get('link')  # Optional link URL
            
            if not board_id:
                return self.format_response(
                    success=False,
                    message="Missing required parameter",
                    error="Board ID is required for Pinterest pins"
                )
            
            if not media_urls or len(media_urls) == 0:
                return self.format_response(
                    success=False,
                    message="Missing required parameter",
                    error="Media URL is required for Pinterest pins"
                )
            
            self.log_post_attempt(content, len(media_urls))
            
            # Validate content
            validation_result = self.validate_content(content, media_urls, **kwargs)
            if not validation_result["valid"]:
                return self.format_response(
                    success=False,
                    message="Content validation failed",
                    error=validation_result["error"]
                )
            
            # Format content for Pinterest
            formatted_content = self.format_pinterest_content(content, **kwargs)
            
            # Post to Pinterest using GetLate service
            result = await asyncio.to_thread(
                self.getlate_service.post_to_pinterest,
                formatted_content,  # Description
                board_id,
                media_urls,  # Media URLs
                link  # Optional link
            )
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, formatted_content)
                return self.format_response(
                    success=True,
                    message="Successfully created Pinterest pin",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to create Pinterest pin",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while creating Pinterest pin: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while creating pin",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get Pinterest account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call Pinterest's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "pinterest",
                "account_id": "pinterest_account",
                "status": "active",
                "followers": 0,  # Would be populated from API
                "following": 0,  # Would be populated from API
                "pins_count": 0,  # Would be populated from API
                "boards_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Pinterest account info: {str(e)}")
            return {
                "platform": "pinterest",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Validate content for Pinterest-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Media URLs to validate
            **kwargs: Additional parameters
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        title = kwargs.get('title', content[:100])
        board_id = kwargs.get('board_id', '')
        link = kwargs.get('link')
        
        # Validate board ID
        if not board_id:
            errors.append("Board ID is required for Pinterest pins")
        
        # Validate title
        if not title or len(title.strip()) == 0:
            errors.append("Title is required for Pinterest pins")
        elif len(title) > self.max_title_length:
            errors.append(f"Title exceeds maximum length of {self.max_title_length} characters")
        
        # Validate description
        if len(content) > self.max_description_length:
            errors.append(f"Description exceeds maximum length of {self.max_description_length} characters")
        
        # Validate media URLs (required for Pinterest)
        if not media_urls or len(media_urls) == 0:
            errors.append("At least one media URL is required for Pinterest pins")
        else:
            for url in media_urls:
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid media URL: {url}")
        
        # Validate link URL if provided
        if link and not link.startswith(('http://', 'https://')):
            errors.append(f"Invalid link URL: {link}")
        
        # Pinterest-specific content guidelines
        if len(content) < 50:
            warnings.append("Pinterest descriptions perform better with more detailed content")
        
        # Check for overly promotional content
        if content.count('buy') + content.count('sale') + content.count('discount') > 3:
            warnings.append("Content may be too promotional for Pinterest's guidelines")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings
        }
    
    def format_pinterest_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for Pinterest
        
        Args:
            content: Raw content (description)
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # Add hashtags if provided (Pinterest supports hashtags)
        hashtags = kwargs.get('hashtags', [])
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            formatted = f"{formatted}\n\n{hashtag_string}"
        
        # Add keywords if provided
        keywords = kwargs.get('keywords', [])
        if keywords:
            keyword_string = ' '.join(keywords)
            formatted = f"{formatted}\n\n{keyword_string}"
        
        return formatted.strip()
    
    def create_board(self, name: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """
        Create a new Pinterest board
        
        Args:
            name: Board name
            description: Board description
            **kwargs: Additional board parameters
            
        Returns:
            Board creation result
        """
        # This would implement Pinterest board creation
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "Pinterest board creation not yet implemented",
            "error": "Board creation requires additional API setup"
        }
    
    def get_board_pins(self, board_id: str, limit: int = 25) -> Dict[str, Any]:
        """
        Get pins from a specific board
        
        Args:
            board_id: Board ID
            limit: Maximum number of pins to retrieve
            
        Returns:
            Board pins information
        """
        # This would implement Pinterest board pins retrieval
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "Pinterest board pins retrieval not yet implemented",
            "error": "Board pins retrieval requires additional API setup"
        }
    
    def optimize_for_search(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Optimize content for Pinterest search
        
        Args:
            content: Original content
            **kwargs: Optimization parameters
            
        Returns:
            Optimized content and suggestions
        """
        # Simple optimization suggestions
        suggestions = []
        
        # Check for keywords
        if len(content.split()) < 10:
            suggestions.append("Add more descriptive keywords")
        
        # Check for hashtags
        if '#' not in content:
            suggestions.append("Consider adding relevant hashtags")
        
        # Check length
        if len(content) < 100:
            suggestions.append("Longer descriptions tend to perform better on Pinterest")
        
        return {
            "success": True,
            "optimized_content": content,
            "suggestions": suggestions
        }