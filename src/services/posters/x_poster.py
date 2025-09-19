"""
X (Twitter) Poster

Handles posting content to X (Twitter) platform.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .base_poster import BasePoster
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

class XPoster(BasePoster):
    """X (Twitter)-specific poster implementation"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize X poster
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        super().__init__("x")
        self.getlate_service = getlate_service
        self.max_tweet_length = 280
        self.max_media_per_tweet = 4
    
    async def post_content(
        self, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to X (Twitter)
        
        Args:
            content: Tweet text content
            media_urls: Optional list of media URLs
            **kwargs: Additional parameters (reply_to, quote_tweet, etc.)
            
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
            
            # Format content for X
            formatted_content = self.format_x_content(content, **kwargs)
            
            # Post to X using GetLate service
            result = await asyncio.to_thread(
                self.getlate_service.post_to_x,
                formatted_content,
                media_urls
            )
            
            if result.get("success"):
                post_id = result.get("post_id", "")
                self.log_post_success(post_id, formatted_content)
                return self.format_response(
                    success=True,
                    message="Successfully posted to X",
                    post_id=post_id,
                    metadata=result
                )
            else:
                error_msg = result.get("error", "Unknown error")
                self.log_post_failure(error_msg)
                return self.format_response(
                    success=False,
                    message="Failed to post to X",
                    error=error_msg,
                    metadata=result
                )
                
        except Exception as e:
            error_msg = f"Exception while posting to X: {str(e)}"
            self.log_post_failure(error_msg)
            return self.format_response(
                success=False,
                message="Exception occurred while posting",
                error=error_msg
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get X account information
        
        Returns:
            Account information
        """
        try:
            # This would typically call X's API to get account info
            # For now, return basic info from GetLate service if available
            return {
                "platform": "x",
                "account_id": "x_account",
                "status": "active",
                "followers": 0,  # Would be populated from API
                "following": 0,  # Would be populated from API
                "tweets_count": 0,  # Would be populated from API
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting X account info: {str(e)}")
            return {
                "platform": "x",
                "status": "error",
                "error": str(e)
            }
    
    def validate_content(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate content for X-specific requirements
        
        Args:
            content: Content to validate
            media_urls: Media URLs to validate
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check tweet length (considering URLs count as 23 characters)
        url_count = content.count('http')
        adjusted_length = len(content) - (url_count * 23) + (url_count * 23)  # URLs count as 23 chars
        
        if adjusted_length > self.max_tweet_length:
            errors.append(f"Tweet exceeds maximum length of {self.max_tweet_length} characters")
        
        # Check media count
        if media_urls and len(media_urls) > self.max_media_per_tweet:
            errors.append(f"Maximum {self.max_media_per_tweet} media files allowed per tweet")
        
        # Validate media URLs
        if media_urls:
            for url in media_urls:
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid media URL: {url}")
        
        # Content warnings
        if len(content) > 200:
            warnings.append("Tweet is quite long, consider shortening for better engagement")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings
        }
    
    def format_x_content(self, content: str, **kwargs) -> str:
        """
        Format content specifically for X (Twitter)
        
        Args:
            content: Raw content
            **kwargs: Formatting options
            
        Returns:
            Formatted content
        """
        formatted = content
        
        # Add hashtags if provided
        hashtags = kwargs.get('hashtags', [])
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            # Add hashtags at the end, ensuring we don't exceed character limit
            if len(formatted) + len(hashtag_string) + 1 <= self.max_tweet_length:
                formatted = f"{formatted} {hashtag_string}"
        
        # Add mentions if provided
        mentions = kwargs.get('mentions', [])
        if mentions:
            mention_string = ' '.join([f"@{mention}" for mention in mentions])
            # Add mentions at the beginning or end based on content
            if len(formatted) + len(mention_string) + 1 <= self.max_tweet_length:
                formatted = f"{mention_string} {formatted}"
        
        return formatted.strip()
    
    def split_long_content(self, content: str, max_length: int = None) -> List[str]:
        """
        Split long content into multiple tweets (thread)
        
        Args:
            content: Long content to split
            max_length: Maximum length per tweet (defaults to platform limit)
            
        Returns:
            List of tweet contents
        """
        max_len = max_length or self.max_tweet_length
        
        if len(content) <= max_len:
            return [content]
        
        # Simple splitting - could be improved with smarter algorithms
        words = content.split()
        tweets = []
        current_tweet = ""
        
        for word in words:
            if len(current_tweet) + len(word) + 1 <= max_len - 10:  # Leave room for tweet number
                current_tweet += f" {word}" if current_tweet else word
            else:
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = word
        
        if current_tweet:
            tweets.append(current_tweet)
        
        # Add tweet numbering if multiple tweets
        if len(tweets) > 1:
            for i, tweet in enumerate(tweets):
                tweets[i] = f"{tweet} ({i+1}/{len(tweets)})"
        
        return tweets