"""
Redis service for caching and session management
"""
import json
import logging
from typing import Optional, Any, Union
import redis.asyncio as redis
from src.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Redis service for caching and session management"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
    
    async def connect(self):
        """Connect to Redis server"""
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30
                )
                # Test connection
                await self.redis_client.ping()
                self.is_connected = True
                logger.info("Connected to Redis successfully")
            else:
                logger.warning("REDIS_URL not configured, Redis caching disabled")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from Redis server"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.is_connected = False
                logger.info("Disconnected from Redis")
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
            else:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, dict, list], 
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration time (seconds)"""
        if not self.is_connected:
            return False
        
        try:
            # Convert dict/list to JSON string if needed
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self.redis_client.setex(key, expire, value)
            logger.debug(f"Cached key {key} with expire {expire}s")
            return bool(result)
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            logger.debug(f"Deleted key {key} from cache")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in Redis: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        if not self.is_connected:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys matching pattern {pattern}")
                return result
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern} from Redis: {e}")
            return 0
    
    async def get_json(self, key: str) -> Optional[Union[dict, list]]:
        """Get JSON value from cache and parse it"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON for key {key}: {e}")
                return None
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Union[dict, list], 
        expire: int = 3600
    ) -> bool:
        """Set JSON value in cache"""
        return await self.set(key, value, expire)
    
    # Cache key generators for different use cases
    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key with prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    def user_session_key(self, user_id: str) -> str:
        """Generate cache key for user session"""
        return self.generate_cache_key("session", user_id)
    
    def workflow_cache_key(self, workflow_id: str) -> str:
        """Generate cache key for workflow data"""
        return self.generate_cache_key("workflow", workflow_id)
    
    def content_cache_key(self, content_type: str, content_id: str) -> str:
        """Generate cache key for content"""
        return self.generate_cache_key("content", content_type, content_id)
    
    def api_response_cache_key(self, endpoint: str, params: str) -> str:
        """Generate cache key for API responses"""
        return self.generate_cache_key("api", endpoint, params)

# Global Redis service instance
redis_service = RedisService()

# Cache decorator for functions
async def cache_result(key: str, expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check cache first
            cached_result = await redis_service.get(key)
            if cached_result:
                return json.loads(cached_result) if cached_result.startswith('{') or cached_result.startswith('[') else cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await redis_service.set(key, result, expire)
            
            return result
        return wrapper
    return decorator