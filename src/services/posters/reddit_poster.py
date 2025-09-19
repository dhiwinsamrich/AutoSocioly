"""
Reddit Poster

Handles posting content to Reddit platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class RedditPoster(BasePoster):
    """Reddit-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize Reddit poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("reddit")
        self.getlate_service = getlate_service
        self.max_title_length = 300
        self.max_selftext_length = 40000
        self.max_media_per_post = 20  # Reddit allows multiple images in galleries
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Reddit
        
        Args:
            content: Post content (can be title + body or URL)
            media_urls: Optional list of media URLs
            **kwargs: Additional parameters (subreddit, post_type, etc.)
            
        Returns:
            Posting result
        """
        try:
            # Extract required parameters
            subreddit = kwargs.get('subreddit')
            if not subreddit:
                return self.format_response(
                    success=False,
                    message="Missing required parameter",
                    error="Subreddit is required for Reddit posts"
                )
            
            post_type = kwargs.get('post_type', 'text')  # text, link, image
            title = kwargs.get('title', content[:200])  # Use first 200 chars as title if not provided
            
            self.log_post_attempt(content, len(media_urls) if media_urls else 0)
            
            # Validate content
            validation_result = self.validate_content(content, media_urls, **kwargs)
            if not validation_result["valid"]:
                return self.format_response(
                    success=False,
                    message="Content validation failed",
                    error=validation_result["error"]
                )
            
            # Format content for Reddit
            formatted_content = self.format_reddit_content(content, **kwargs)
            
            # Post to Reddit using GetLate service
            result = await asyncio.to_thread(
                self.getlate_service.post_to_reddit,
                formatted_content,  # This will be the title
                subreddit,
                media_urls[0] if media_urls and post_type == 'link' else None  # URL for link posts
            )
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, formatted_content)
                return self.format_response(
                    success=True,
                    message="Successfully posted to Reddit",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to post to Reddit",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while posting to Reddit: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while posting",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get Reddit account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call Reddit's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "reddit",
                "account_id": "reddit_account",
                "status": "active",
                "karma": 0,  # Would be populated from API
                "cake_day": None,  # Would be populated from API
                "posts_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Reddit account info: {str(e)}")
            return {
                "platform": "reddit",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Validate content for Reddit-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Media URLs to validate
            **kwargs: Additional parameters
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        post_type = kwargs.get('post_type', 'text')
        title = kwargs.get('title', content[:200])
        subreddit = kwargs.get('subreddit', '')
        
        # Validate subreddit
        if not subreddit:
            errors.append("Subreddit is required")
        elif not subreddit.startswith('r/'):
            # Auto-add r/ prefix if missing
            subreddit = f"r/{subreddit}"
        
        # Validate title
        if not title or len(title.strip()) == 0:
            errors.append("Title is required for Reddit posts")
        elif len(title) > self.max_title_length:
            errors.append(f"Title exceeds maximum length of {self.max_title_length} characters")
        
        # Validate based on post type
        if post_type == 'text':
            if len(content) > self.max_selftext_length:
                errors.append(f"Text post exceeds maximum length of {self.max_selftext_length} characters")
        elif post_type == 'link':
            if not media_urls or len(media_urls) == 0:
                errors.append("Link posts require a URL")
        elif post_type == 'image':
            if not media_urls or len(media_urls) == 0:
                errors.append("Image posts require at least one image")
        
        # Check media count
        if media_urls and len(media_urls) > self.max_media_per_post:
            errors.append(f"Maximum {self.max_media_per_post} media files allowed per post")
        
        # Validate media URLs
        if media_urls:
            for url in media_urls:
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid media URL: {url}")
        
        # Reddit-specific content guidelines
        if len(title) < 10:
            warnings.append("Title is quite short, consider making it more descriptive")
        
        # Check for potential spam indicators
        if len(content) < 50 and not media_urls:
            warnings.append("Very short text posts may be considered low-quality")
        
        # Check for excessive caps
        if sum(1 for c in title if c.isupper()) / len(title) > 0.5:
            warnings.append("Title contains excessive capitalization")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings
        }
    
    def format_reddit_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for Reddit
        
        Args:
            content: Raw content
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # For Reddit, the main content becomes the title for most post types
        post_type = kwargs.get('post_type', 'text')
        
        if post_type == 'text':
            # For text posts, use the provided title or first part of content as title
            # and the rest as the body text
            title = kwargs.get('title', content[:200])
            if len(content) > len(title):
                # The content after the title would be the body text
                pass
        
        # Add formatting for better readability
        formatted = formatted.strip()
        
        # Ensure proper line breaks for readability
        if '\n' not in formatted and len(formatted) > 200:
            # Add some line breaks for long text
            words = formatted.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 > 80:  # Roughly 80 chars per line
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line += f" {word}" if current_line else word
            
            if current_line:
                lines.append(current_line)
            
            formatted = '\n\n'.join(lines)
        
        return formatted
    
    def get_subreddit_rules(self, subreddit: str) -> Dict[str, Any]:
        """
        Get subreddit-specific rules and guidelines
        
        Args:
            subreddit: Subreddit name
            
        Returns:
            Subreddit rules and guidelines
        """
        # This would implement Reddit API call to get subreddit rules
        # For now, return a placeholder implementation
        return {
            "success": False,
            "message": "Subreddit rules retrieval not yet implemented",
            "error": "Requires Reddit API integration"
        }
    
    def format_subreddit_name(self, subreddit: str) -> str:
        """
        Format and validate subreddit name
        
        Args:
            subreddit: Raw subreddit name
            
        Returns:
            Formatted subreddit name
        """
        if not subreddit:
            return ""
        
        # Remove r/ prefix if it exists, then add it back
        subreddit = subreddit.replace('r/', '').strip()
        
        # Remove any invalid characters
        import re
        subreddit = re.sub(r'[^a-zA-Z0-9_]', '', subreddit)
        
        return f"r/{subreddit}" if subreddit else ""