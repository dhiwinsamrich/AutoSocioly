"""
Poster Service

Manages platform-specific posters and handles content posting across different social media platforms.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from .posters.base_poster import BasePoster, PosterFactory
from .posters.instagram_poster import InstagramPoster
from .posters.x_poster import XPoster
from .posters.facebook_poster import FacebookPoster
from .posters.linkedin_poster import LinkedInPoster
from .posters.reddit_poster import RedditPoster
from .posters.pinterest_poster import PinterestPoster
from .getlate_service import GetLateService
from ..utils.logger_config import get_logger

class PosterService:
    """Service for managing platform-specific posters"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize the poster service
        
        Args:
            getlate_service: GetLate service instance for API calls
        """
        self.getlate_service = getlate_service
        self.logger = get_logger('poster_service')
        self._posters: Dict[str, BasePoster] = {}
        
        # Register all platform posters
        self._register_posters()
    
    def _register_posters(self):
        """Register all platform-specific poster classes"""
        PosterFactory.register_poster("instagram", InstagramPoster)
        PosterFactory.register_poster("x", XPoster)
        PosterFactory.register_poster("twitter", XPoster)  # Alias for X
        PosterFactory.register_poster("facebook", FacebookPoster)
        PosterFactory.register_poster("linkedin", LinkedInPoster)
        PosterFactory.register_poster("reddit", RedditPoster)
        PosterFactory.register_poster("pinterest", PinterestPoster)
        
        self.logger.info("Registered all platform posters")
    
    def get_poster(self, platform: str) -> Optional[BasePoster]:
        """
        Get a poster instance for the specified platform
        
        Args:
            platform: Platform name
            
        Returns:
            Platform poster instance or None if not supported
        """
        platform_lower = platform.lower()
        
        # Create poster instance if not already cached
        if platform_lower not in self._posters:
            try:
                poster = PosterFactory.create_poster(platform_lower, self.getlate_service)
                self._posters[platform_lower] = poster
                self.logger.info(f"Created poster for platform: {platform}")
            except ValueError as e:
                self.logger.error(f"Failed to create poster for platform {platform}: {str(e)}")
                return None
        
        return self._posters.get(platform_lower)
    
    async def post_to_platform(
        self, 
        platform: str, 
        content: str, 
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to a specific platform
        
        Args:
            platform: Target platform name
            content: Content to post
            media_urls: Optional list of media URLs
            **kwargs: Platform-specific parameters
            
        Returns:
            Posting result
        """
        start_time = datetime.utcnow()
        workflow_logger = get_logger('workflow')
        platform_logger = get_logger(f'platform.{platform}')
        
        poster = self.get_poster(platform)
        if not poster:
            error_msg = f"Unsupported platform: {platform}"
            self.logger.error(error_msg)
            platform_logger.error(f"POST ERROR: Platform not supported", extra={
                'action': 'platform_error',
                'error': error_msg
            })
            return {
                "success": False,
                "platform": platform,
                "message": error_msg,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            self.logger.info(f"Posting to {platform} - Content length: {len(content)}")
            platform_logger.info(f"POST START: {platform}", extra={
                'action': 'post_start',
                'platform': platform,
                'content_length': len(content),
                'has_media': bool(media_urls),
                'media_count': len(media_urls) if media_urls else 0
            })
            
            result = await poster.post_content(content, media_urls, **kwargs)
            success = result.get("success", False)
            post_id = result.get("post_id", "unknown")
            
            total_duration = (datetime.utcnow() - start_time).total_seconds()
            
            if success:
                self.logger.info(f"Successfully posted to {platform}")
                platform_logger.info(f"POST SUCCESS: {platform}", extra={
                    'action': 'post_success',
                    'duration': total_duration,
                    'post_id': post_id,
                    'platform': platform
                })
                
                workflow_logger.info(f"Platform posting success: {platform}", extra={
                    'action': 'platform_post_success',
                    'platform': platform,
                    'duration': total_duration,
                    'post_id': post_id
                })
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to post to {platform}: {error_msg}")
                platform_logger.error(f"POST FAILED: {platform}", extra={
                    'action': 'post_failed',
                    'duration': total_duration,
                    'error': error_msg,
                    'platform': platform
                })
                
                workflow_logger.error(f"Platform posting failed: {platform}", extra={
                    'action': 'platform_post_failed',
                    'platform': platform,
                    'duration': total_duration,
                    'error': error_msg
                })
            
            return result
            
        except Exception as e:
            total_duration = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Exception while posting to {platform}: {str(e)}"
            self.logger.error(error_msg)
            platform_logger.error(f"POST ERROR: Exception occurred", extra={
                'action': 'post_exception',
                'duration': total_duration,
                'error': str(e),
                'error_type': type(e).__name__
            })
            return {
                "success": False,
                "platform": platform,
                "message": "Exception occurred while posting",
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def post_to_multiple_platforms(
        self, 
        platforms: List[str], 
        content: str, 
        media_urls: Optional[List[str]] = None,
        platform_configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Post content to multiple platforms simultaneously
        
        Args:
            platforms: List of target platform names
            content: Content to post
            media_urls: Optional list of media URLs
            platform_configs: Platform-specific configurations
            
        Returns:
            Results for all platforms
        """
        self.logger.info(f"Posting to multiple platforms: {platforms}")
        
        # Default platform configs if not provided
        if platform_configs is None:
            platform_configs = {}
        
        # Create posting tasks for all platforms
        tasks = []
        for platform in platforms:
            config = platform_configs.get(platform, {})
            task = self.post_to_platform(platform, content, media_urls, **config)
            tasks.append(task)
        
        # Execute all posting tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        platform_results = {}
        overall_success = True
        
        for platform, result in zip(platforms, results):
            if isinstance(result, Exception):
                platform_results[platform] = {
                    "success": False,
                    "platform": platform,
                    "message": "Exception occurred",
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_success = False
            else:
                platform_results[platform] = result
                if not result.get("success", False):
                    overall_success = False
        
        return {
            "success": overall_success,
            "platform_results": platform_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def validate_content_for_platforms(
        self, 
        platforms: List[str], 
        content: str, 
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate content for multiple platforms
        
        Args:
            platforms: List of platform names
            content: Content to validate
            media_urls: Optional media URLs
            
        Returns:
            Validation results for all platforms
        """
        self.logger.info(f"Validating content for platforms: {platforms}")
        
        validation_results = {}
        all_valid = True
        
        for platform in platforms:
            poster = self.get_poster(platform)
            if poster:
                validation_result = poster.validate_content(content, media_urls)
                validation_results[platform] = validation_result
                if not validation_result.get("valid", False):
                    all_valid = False
            else:
                validation_results[platform] = {
                    "valid": False,
                    "error": f"Unsupported platform: {platform}"
                }
                all_valid = False
        
        return {
            "valid": all_valid,
            "platform_validations": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_platform_accounts_info(self, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get account information for multiple platforms
        
        Args:
            platforms: Optional list of specific platforms, or None for all
            
        Returns:
            Account information for all requested platforms
        """
        if platforms is None:
            platforms = PosterFactory.get_supported_platforms()
        
        self.logger.info(f"Getting account info for platforms: {platforms}")
        
        # Create tasks for getting account info
        tasks = []
        target_platforms = []
        
        for platform in platforms:
            poster = self.get_poster(platform)
            if poster:
                task = poster.get_account_info()
                tasks.append(task)
                target_platforms.append(platform)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        accounts_info = {}
        for platform, result in zip(target_platforms, results):
            if isinstance(result, Exception):
                accounts_info[platform] = {
                    "platform": platform,
                    "status": "error",
                    "error": str(result)
                }
            else:
                accounts_info[platform] = result
        
        return {
            "accounts": accounts_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platforms
        
        Returns:
            List of supported platform names
        """
        return PosterFactory.get_supported_platforms()
    
    def is_platform_supported(self, platform: str) -> bool:
        """
        Check if a platform is supported
        
        Args:
            platform: Platform name to check
            
        Returns:
            True if platform is supported, False otherwise
        """
        return platform.lower() in PosterFactory.get_supported_platforms()
    
    def get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """
        Get requirements and limitations for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            Platform requirements and limitations
        """
        poster = self.get_poster(platform)
        if not poster:
            return {
                "supported": False,
                "error": f"Platform {platform} is not supported"
            }
        
        # Return platform-specific requirements
        requirements = {
            "supported": True,
            "platform": platform,
            "requirements": {}
        }
        
        # Add platform-specific requirements based on poster type
        if isinstance(poster, InstagramPoster):
            requirements["requirements"] = {
                "media_required": True,
                "max_caption_length": 2200,
                "max_media_per_post": 10,
                "allowed_media_types": ["image/jpeg", "image/png", "image/jpg"]
            }
        elif isinstance(poster, XPoster):
            requirements["requirements"] = {
                "media_required": False,
                "max_content_length": 280,
                "max_media_per_post": 4,
                "supports_threads": True
            }
        elif isinstance(poster, FacebookPoster):
            requirements["requirements"] = {
                "media_required": False,
                "max_content_length": 63206,
                "max_media_per_post": 50,
                "supports_stories": True
            }
        elif isinstance(poster, LinkedInPoster):
            requirements["requirements"] = {
                "media_required": False,
                "max_content_length": 3000,
                "max_media_per_post": 9,
                "professional_focus": True
            }
        elif isinstance(poster, RedditPoster):
            requirements["requirements"] = {
                "subreddit_required": True,
                "max_title_length": 300,
                "max_content_length": 40000,
                "max_media_per_post": 20
            }
        elif isinstance(poster, PinterestPoster):
            requirements["requirements"] = {
                "board_id_required": True,
                "media_required": True,
                "max_description_length": 500,
                "max_title_length": 100
            }
        
        return requirements