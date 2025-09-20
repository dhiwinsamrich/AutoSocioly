"""
Authentication Service - Handles proper authentication for all social media platforms
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path

from ..models import Platform
from .getlate_service import GetLateService
from ..utils.ngrok_manager import NgrokManager

logger = logging.getLogger(__name__)

class PlatformAuthConfig:
    """Platform-specific authentication configurations"""
    
    PLATFORM_CONFIGS = {
        Platform.REDDIT: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "platform_specific_fields": ["subreddit", "url"],
            "example_config": {
                "platform": "reddit",
                "accountId": "REDDIT_ACCOUNT_ID",
                "platformSpecificData": {
                    "subreddit": "reactjs",
                    "url": "https://example.com/article"
                }
            }
        },
        Platform.INSTAGRAM: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "requires_media": True,
            "platform_specific_fields": ["caption", "location", "hashtags"],
            "example_config": {
                "platform": "instagram",
                "accountId": "INSTAGRAM_ACCOUNT_ID",
                "platformSpecificData": {
                    "caption": "Check out this amazing content!",
                    "hashtags": ["#tech", "#innovation"]
                }
            }
        },
        Platform.FACEBOOK: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "platform_specific_fields": ["privacy", "targeting", "link"],
            "example_config": {
                "platform": "facebook",
                "accountId": "FACEBOOK_ACCOUNT_ID",
                "platformSpecificData": {
                    "privacy": "public",
                    "link": "https://example.com/article"
                }
            }
        },
        Platform.LINKEDIN: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "platform_specific_fields": ["visibility", "article_url"],
            "example_config": {
                "platform": "linkedin",
                "accountId": "LINKEDIN_ACCOUNT_ID",
                "platformSpecificData": {
                    "visibility": "public",
                    "article_url": "https://example.com/article"
                }
            }
        },
        Platform.X: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "platform_specific_fields": ["hashtags", "mentions"],
            "example_config": {
                "platform": "x",
                "accountId": "X_ACCOUNT_ID",
                "platformSpecificData": {
                    "hashtags": ["#tech", "#ai"]
                }
            }
        },
        Platform.TWITTER: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "platform_specific_fields": ["hashtags", "mentions"],
            "example_config": {
                "platform": "twitter",
                "accountId": "TWITTER_ACCOUNT_ID",
                "platformSpecificData": {
                    "hashtags": ["#tech", "#ai"]
                }
            }
        },
        Platform.PINTEREST: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "requires_media": True,
            "platform_specific_fields": ["board", "description", "link"],
            "example_config": {
                "platform": "pinterest",
                "accountId": "PINTEREST_ACCOUNT_ID",
                "platformSpecificData": {
                    "board": "technology",
                    "description": "Amazing tech content",
                    "link": "https://example.com/article"
                }
            }
        },
        Platform.TIKTOK: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "requires_media": True,
            "platform_specific_fields": ["description", "hashtags"],
            "example_config": {
                "platform": "tiktok",
                "accountId": "TIKTOK_ACCOUNT_ID",
                "platformSpecificData": {
                    "description": "Check out this amazing video!",
                    "hashtags": ["#tech", "#innovation"]
                }
            }
        },
        Platform.YOUTUBE: {
            "auth_type": "bearer",
            "endpoint": "/posts",
            "requires_account_id": True,
            "requires_media": True,
            "platform_specific_fields": ["title", "description", "tags", "category"],
            "example_config": {
                "platform": "youtube",
                "accountId": "YOUTUBE_ACCOUNT_ID",
                "platformSpecificData": {
                    "title": "Amazing Tech Video",
                    "description": "Check out this amazing content!",
                    "tags": ["tech", "innovation"]
                }
            }
        }
    }

class AuthService:
    """Handles proper authentication for all social media platforms"""
    
    def __init__(self, getlate_service: GetLateService):
        """
        Initialize authentication service
        
        Args:
            getlate_service: GetLate service instance
        """
        self.getlate_service = getlate_service
        self.ngrok_manager = NgrokManager()
        logger.info("Authentication service initialized")
    
    def get_platform_auth_config(self, platform: Platform) -> Dict[str, Any]:
        """
        Get authentication configuration for a specific platform
        
        Args:
            platform: Target platform
            
        Returns:
            Platform authentication configuration
        """
        config = PlatformAuthConfig.PLATFORM_CONFIGS.get(platform, {})
        if not config:
            logger.warning(f"No authentication configuration found for platform: {platform}")
        return config
    
    def create_authenticated_post_data(
        self,
        content: str,
        platforms: List[Platform],
        media_urls: Optional[List[str]] = None,
        platform_configs: Optional[Dict[Platform, Dict[str, Any]]] = None,
        account_mappings: Optional[Dict[Platform, str]] = None
    ) -> Dict[str, Any]:
        """
        Create properly formatted post data with authentication
        
        Args:
            content: Post content
            platforms: List of target platforms
            media_urls: Optional media URLs
            platform_configs: Platform-specific configurations
            account_mappings: Platform to account ID mappings
            
        Returns:
            Formatted post data for GetLate API
        """
        platform_configs = platform_configs or {}
        account_mappings = account_mappings or {}
        
        # Build platform configurations
        platform_data = []
        
        for platform in platforms:
            auth_config = self.get_platform_auth_config(platform)
            if not auth_config:
                logger.warning(f"Skipping platform {platform} - no auth config")
                continue
            
            # Get account ID for platform
            account_id = account_mappings.get(platform)
            if not account_id and auth_config.get("requires_account_id"):
                logger.warning(f"No account ID provided for platform {platform}")
                continue
            
            # Build platform-specific data
            platform_specific_data = {}
            
            # Add user-provided platform config
            if platform in platform_configs:
                platform_specific_data.update(platform_configs[platform])
            
            # Add required platform-specific fields
            required_fields = auth_config.get("platform_specific_fields", [])
            for field in required_fields:
                if field not in platform_specific_data:
                    # Add default values for required fields
                    if field == "subreddit":
                        platform_specific_data[field] = "technology"
                    elif field == "hashtags":
                        platform_specific_data[field] = ["#content", "#social"]
                    elif field == "caption":
                        platform_specific_data[field] = content[:200]
                    elif field == "description":
                        platform_specific_data[field] = content[:500]
                    elif field == "title":
                        platform_specific_data[field] = content[:100]
                    elif field == "privacy" or field == "visibility":
                        platform_specific_data[field] = "public"
            
            # Create platform configuration
            platform_entry = {
                "platform": platform.value,
                "accountId": account_id
            }
            
            if platform_specific_data:
                platform_entry["platformSpecificData"] = platform_specific_data
            
            platform_data.append(platform_entry)
            logger.info(f"Created auth config for {platform.value} with account {account_id}")
        
        # Create final post data
        post_data = {
            "content": content,
            "platforms": platform_data
        }
        
        # Add media items if provided
        if media_urls:
            media_items = []
            for url in media_urls:
                media_item = {
                    "type": "image",
                    "url": url
                }
                media_items.append(media_item)
            post_data["media_items"] = media_items
        
        return post_data
    
    def make_public_media_urls(self, media_paths: List[str]) -> List[str]:
        """
        Convert local media paths to public URLs using ngrok
        
        Args:
            media_paths: List of local media file paths
            
        Returns:
            List of public URLs
        """
        public_urls = []
        
        for media_path in media_paths:
            try:
                # Create public URL using ngrok
                public_url = self.ngrok_manager.create_public_url(media_path)
                if public_url:
                    public_urls.append(public_url)
                    logger.info(f"Created public URL for {media_path}: {public_url}")
                else:
                    logger.warning(f"Failed to create public URL for {media_path}")
                    
            except Exception as e:
                logger.error(f"Error creating public URL for {media_path}: {e}")
        
        return public_urls
    
    def get_example_curl_commands(self, api_key: str, base_url: str = "https://getlate.dev/api/v1") -> Dict[str, str]:
        """
        Generate example cURL commands for all platforms
        
        Args:
            api_key: GetLate API key
            base_url: API base URL
            
        Returns:
            Dictionary of platform to cURL command examples
        """
        examples = {}
        
        for platform in Platform:
            auth_config = self.get_platform_auth_config(platform)
            if not auth_config:
                continue
            
            # Create example data
            example_data = {
                "content": f"Discussion thread for our latest {platform.value} content",
                "platforms": [auth_config["example_config"]]
            }
            
            # Add media if required
            if auth_config.get("requires_media"):
                example_data["media_items"] = [{
                    "type": "image",
                    "url": "https://example.com/image.jpg"
                }]
            
            # Build cURL command
            curl_command = f"""# {platform.value.title()} Post Example
curl -X POST '{base_url}{auth_config['endpoint']}' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(example_data, indent=2)}'"""
            
            examples[platform.value] = curl_command
        
        return examples
    
    def validate_platform_requirements(
        self,
        platform: Platform,
        content: str,
        media_urls: Optional[List[str]] = None,
        platform_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate platform-specific requirements
        
        Args:
            platform: Target platform
            content: Post content
            media_urls: Optional media URLs
            platform_config: Platform-specific configuration
            
        Returns:
            Validation result
        """
        auth_config = self.get_platform_auth_config(platform)
        if not auth_config:
            return {
                "valid": False,
                "error": f"No authentication configuration for platform: {platform}"
            }
        
        errors = []
        warnings = []
        
        # Check media requirements
        if auth_config.get("requires_media") and not media_urls:
            errors.append(f"{platform.value} requires media items (images/videos)")
        
        # Check content length requirements (platform-specific)
        content_limits = {
            Platform.X: 280,
            Platform.TWITTER: 280,
            Platform.INSTAGRAM: 2200,
            Platform.REDDIT: 40000,
            Platform.LINKEDIN: 3000,
            Platform.FACEBOOK: 63206
        }
        
        max_length = content_limits.get(platform)
        if max_length and len(content) > max_length:
            errors.append(f"Content exceeds {platform.value} maximum length of {max_length} characters")
        
        # Check platform-specific configuration
        if platform_config:
            required_fields = auth_config.get("platform_specific_fields", [])
            for field in required_fields:
                if field not in platform_config and field not in ["hashtags", "mentions", "caption", "description"]:
                    warnings.append(f"Recommended field '{field}' not provided for {platform.value}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "platform_config": auth_config
        }