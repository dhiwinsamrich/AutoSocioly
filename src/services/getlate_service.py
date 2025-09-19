import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from urllib.parse import urljoin

from ..models import Platform, GetLatePostData, GetLateAccount
from ..utils.logger_config import log_api_call, log_social_media_action

logger = logging.getLogger(__name__)

class GetLateAPIError(Exception):
    """Custom exception for GetLate API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Any = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

class GetLateService:
    """Service for interacting with GetLate API"""
    
    def __init__(self, api_key: str, base_url: str = "https://getlate.dev/api/v1"):
        """
        Initialize GetLate service
        
        Args:
            api_key: GetLate API key
            base_url: GetLate API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'GetLate-SocialMediaAutomation/1.0.0'
        })
        
        logger.info(f"GetLate service initialized with base URL: {self.base_url}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make HTTP request to GetLate API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            files: Files to upload
            timeout: Request timeout
            
        Returns:
            API response data
            
        Raises:
            GetLateAPIError: If API request fails
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        start_time = time.time()
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            if files:
                # Remove Content-Type header for multipart uploads
                headers = self.session.headers.copy()
                headers.pop('Content-Type', None)
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    files=files,
                    params=params,
                    timeout=timeout,
                    headers=headers
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=timeout
                )
            
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log API call
            log_api_call(
                logger_name='getlate.api',
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration
            )
            
            logger.debug(f"Response status: {response.status_code}, duration: {duration:.2f}ms")
            
            # Handle different response status codes
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"message": response.text}
            
            elif response.status_code == 201:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"message": "Resource created successfully"}
            
            elif response.status_code == 204:
                return {"message": "Operation completed successfully"}
            
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                raise GetLateAPIError(
                    f"Bad request: {error_data.get('message', 'Invalid request')}",
                    status_code=400,
                    response_data=error_data
                )
            
            elif response.status_code == 401:
                raise GetLateAPIError(
                    "Authentication failed: Invalid API key",
                    status_code=401
                )
            
            elif response.status_code == 403:
                error_data = response.json() if response.text else {}
                raise GetLateAPIError(
                    f"Forbidden: {error_data.get('message', 'Access denied')}",
                    status_code=403,
                    response_data=error_data
                )
            
            elif response.status_code == 404:
                raise GetLateAPIError(
                    "Resource not found",
                    status_code=404
                )
            
            elif response.status_code == 429:
                error_data = response.json() if response.text else {}
                raise GetLateAPIError(
                    f"Rate limit exceeded: {error_data.get('message', 'Too many requests')}",
                    status_code=429,
                    response_data=error_data
                )
            
            elif response.status_code >= 500:
                error_data = response.json() if response.text else {}
                raise GetLateAPIError(
                    f"Server error: {error_data.get('message', 'Internal server error')}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            else:
                raise GetLateAPIError(
                    f"Unexpected status code: {response.status_code}",
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {method} {url}")
            raise GetLateAPIError(f"Request timeout after {timeout} seconds", status_code=408)
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {method} {url}: {e}")
            raise GetLateAPIError(f"Connection error: {str(e)}", status_code=503)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {method} {url}: {e}")
            raise GetLateAPIError(f"Request error: {str(e)}", status_code=500)
    
    # Account Management
    def get_accounts(self) -> List[GetLateAccount]:
        """
        Get all connected accounts
        
        Returns:
            List of connected accounts
        """
        try:
            response = self._make_request('GET', '/accounts')
            accounts = []
            
            for account_data in response.get('accounts', []):
                account = GetLateAccount(
                    id=account_data['id'],
                    platform=Platform(account_data['platform']),
                    name=account_data['name'],
                    username=account_data.get('username'),
                    connected=account_data.get('connected', True),
                    last_used=datetime.fromisoformat(account_data['last_used']) if account_data.get('last_used') else None
                )
                accounts.append(account)
            
            logger.info(f"Retrieved {len(accounts)} connected accounts")
            return accounts
            
        except GetLateAPIError as e:
            logger.error(f"Failed to get accounts: {e}")
            raise
    
    def get_account_by_platform(self, platform: Platform) -> Optional[GetLateAccount]:
        """
        Get account for specific platform
        
        Args:
            platform: Target platform
            
        Returns:
            Account information or None if not found
        """
        accounts = self.get_accounts()
        for account in accounts:
            if account.platform == platform:
                return account
        return None
    
    # Posting
    def create_post(self, post_data: GetLatePostData) -> Dict[str, Any]:
        """
        Create a new post
        
        Args:
            post_data: Post data
            
        Returns:
            Created post information
        """
        try:
            response = self._make_request('POST', '/posts', data=post_data.dict(exclude_none=True))
            logger.info(f"Post created successfully: {response.get('id', 'unknown')}")
            return response
            
        except GetLateAPIError as e:
            logger.error(f"Failed to create post: {e}")
            raise
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get post by ID
        
        Args:
            post_id: Post ID
            
        Returns:
            Post information
        """
        try:
            response = self._make_request('GET', f'/posts/{post_id}')
            return response
            
        except GetLateAPIError as e:
            logger.error(f"Failed to get post {post_id}: {e}")
            raise
    
    def get_posts(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get posts with pagination
        
        Args:
            limit: Number of posts to retrieve
            offset: Offset for pagination
            
        Returns:
            List of posts
        """
        try:
            params = {'limit': limit, 'offset': offset}
            response = self._make_request('GET', '/posts', params=params)
            return response.get('posts', [])
            
        except GetLateAPIError as e:
            logger.error(f"Failed to get posts: {e}")
            raise
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete post by ID
        
        Args:
            post_id: Post ID
            
        Returns:
            True if successful
        """
        try:
            self._make_request('DELETE', f'/posts/{post_id}')
            logger.info(f"Post {post_id} deleted successfully")
            return True
            
        except GetLateAPIError as e:
            logger.error(f"Failed to delete post {post_id}: {e}")
            raise
    
    # Platform-specific methods
    def post_to_facebook(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post to Facebook
        
        Args:
            content: Post content
            media_urls: Optional media URLs
            
        Returns:
            Post result
        """
        post_data = {
            "content": content,
            "platforms": [{"platform": "facebook"}]
        }
        
        if media_urls:
            post_data["mediaItems"] = [{"type": "image", "url": url} for url in media_urls]
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('facebook', 'post', True, post_id=result.get('id'))
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('facebook', 'post', False, error=str(e))
            raise
    
    def post_to_instagram(self, content: str, media_urls: List[str]) -> Dict[str, Any]:
        """
        Post to Instagram
        
        Args:
            content: Post content
            media_urls: Media URLs (required for Instagram)
            
        Returns:
            Post result
        """
        if not media_urls:
            raise ValueError("Instagram posts require at least one media URL")
        
        post_data = {
            "content": content,
            "platforms": [{"platform": "instagram"}],
            "mediaItems": [{"type": "image", "url": url} for url in media_urls]
        }
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('instagram', 'post', True, post_id=result.get('id'))
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('instagram', 'post', False, error=str(e))
            raise
    
    def post_to_linkedin(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post to LinkedIn
        
        Args:
            content: Post content
            media_urls: Optional media URLs
            
        Returns:
            Post result
        """
        post_data = {
            "content": content,
            "platforms": [{"platform": "linkedin"}]
        }
        
        if media_urls:
            post_data["mediaItems"] = [{"type": "image", "url": url} for url in media_urls]
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('linkedin', 'post', True, post_id=result.get('id'))
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('linkedin', 'post', False, error=str(e))
            raise
    
    def post_to_x(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post to X (Twitter)
        
        Args:
            content: Post content
            media_urls: Optional media URLs
            
        Returns:
            Post result
        """
        post_data = {
            "content": content,
            "platforms": [{"platform": "x"}]
        }
        
        if media_urls:
            post_data["mediaItems"] = [{"type": "image", "url": url} for url in media_urls]
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('x', 'post', True, post_id=result.get('id'))
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('x', 'post', False, error=str(e))
            raise
    
    def post_to_reddit(self, content: str, subreddit: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Reddit
        
        Args:
            content: Post content
            subreddit: Target subreddit
            url: Optional URL for link posts
            
        Returns:
            Post result
        """
        post_data = {
            "content": content,
            "platforms": [{
                "platform": "reddit",
                "platformSpecificData": {
                    "subreddit": subreddit
                }
            }]
        }
        
        if url:
            post_data["platforms"][0]["platformSpecificData"]["url"] = url
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('reddit', 'post', True, post_id=result.get('id'), subreddit=subreddit)
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('reddit', 'post', False, error=str(e), subreddit=subreddit)
            raise
    
    def post_to_pinterest(self, content: str, board_id: str, media_urls: List[str], link: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Pinterest
        
        Args:
            content: Post content
            board_id: Target board ID
            media_urls: Media URLs
            link: Optional destination link
            
        Returns:
            Post result
        """
        if not media_urls:
            raise ValueError("Pinterest posts require at least one media URL")
        
        post_data = {
            "content": content,
            "platforms": [{
                "platform": "pinterest",
                "platformSpecificData": {
                    "boardId": board_id
                }
            }],
            "mediaItems": [{"type": "image", "url": url} for url in media_urls]
        }
        
        if link:
            post_data["platforms"][0]["platformSpecificData"]["link"] = link
        
        try:
            result = self.create_post(GetLatePostData(**post_data))
            log_social_media_action('pinterest', 'post', True, post_id=result.get('id'), board_id=board_id)
            return result
            
        except GetLateAPIError as e:
            log_social_media_action('pinterest', 'post', False, error=str(e), board_id=board_id)
            raise
    
    # Analytics and Insights
    def get_analytics(self, platform: Optional[Platform] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analytics data
        
        Args:
            platform: Optional platform filter
            date_from: Optional start date (ISO format)
            date_to: Optional end date (ISO format)
            
        Returns:
            Analytics data
        """
        params = {}
        if platform:
            params['platform'] = platform.value
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        try:
            response = self._make_request('GET', '/analytics', params=params)
            return response
            
        except GetLateAPIError as e:
            logger.error(f"Failed to get analytics: {e}")
            raise