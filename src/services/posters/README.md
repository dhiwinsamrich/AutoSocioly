# Social Media Posters

This package provides platform-specific poster implementations for different social media platforms. Each poster handles the unique requirements and APIs of its respective platform.

## Overview

The poster system consists of:

1. **BasePoster** - Abstract base class defining the common interface
2. **Platform-specific posters** - Individual implementations for each platform
3. **PosterService** - Main service for managing and coordinating posters
4. **PosterFactory** - Factory pattern for creating poster instances

## Supported Platforms

- **Instagram** (`instagram_poster.py`) - Photo and video sharing
- **X (Twitter)** (`x_poster.py`) - Microblogging and social networking
- **Facebook** (`facebook_poster.py`) - Social networking and sharing
- **LinkedIn** (`linkedin_poster.py`) - Professional networking
- **Reddit** (`reddit_poster.py`) - Community discussion and sharing
- **Pinterest** (`pinterest_poster.py`) - Visual discovery and bookmarking

## Architecture

```
posters/
├── __init__.py              # Package initialization and exports
├── base_poster.py           # Abstract base class and factory
├── instagram_poster.py      # Instagram-specific implementation
├── x_poster.py             # X (Twitter) implementation
├── facebook_poster.py       # Facebook implementation
├── linkedin_poster.py       # LinkedIn implementation
├── reddit_poster.py         # Reddit implementation
├── pinterest_poster.py      # Pinterest implementation
├── usage_example.py         # Comprehensive usage examples
└── README.md               # This file
```

## Quick Start

### Basic Usage

```python
from src.services.poster_service import PosterService
from src.services.getlate_service import GetLateService

# Initialize services
getlate_service = GetLateService()
poster_service = PosterService(getlate_service)

# Post to a single platform
result = await poster_service.post_to_platform(
    platform="instagram",
    content="Amazing sunset! 🌅 #photography #nature",
    media_urls=["https://example.com/sunset.jpg"],
    hashtags=["photography", "nature", "sunset"],
    location="Malibu, CA"
)
```

### Multi-Platform Posting

```python
# Post to multiple platforms simultaneously
platforms = ["x", "facebook", "linkedin"]
platform_configs = {
    "x": {"hashtags": ["tech", "ai"]},
    "facebook": {"feeling": "excited"},
    "linkedin": {"article_url": "https://example.com/article"}
}

results = await poster_service.post_to_multiple_platforms(
    platforms=platforms,
    content="New AI breakthrough announced!",
    media_urls=["https://example.com/ai-image.jpg"],
    platform_configs=platform_configs
)
```

### Content Validation

```python
# Validate content before posting
validation_result = await poster_service.validate_content_for_platforms(
    platforms=["x", "instagram", "facebook"],
    content="Your content here...",
    media_urls=["https://example.com/image.jpg"]
)

if validation_result["valid"]:
    print("Content is valid for all platforms!")
else:
    for platform, result in validation_result["platform_validations"].items():
        if not result["valid"]:
            print(f"{platform}: {result['error']}")
```

## Platform-Specific Features

### Instagram
- **Media Required**: Yes (photos/videos)
- **Max Caption**: 2,200 characters
- **Max Media**: 10 items per post
- **Features**: Hashtags, location tags, mentions

### X (Twitter)
- **Media Required**: No
- **Max Characters**: 280
- **Max Media**: 4 items per tweet
- **Features**: Hashtags, mentions, thread support

### Facebook
- **Media Required**: No
- **Max Characters**: 63,206
- **Max Media**: 50 items per post
- **Features**: Hashtags, feelings, location, story creation

### LinkedIn
- **Media Required**: No
- **Max Characters**: 3,000
- **Max Media**: 9 items per post
- **Features**: Professional hashtags, article links, company posting

### Reddit
- **Subreddit Required**: Yes
- **Max Title**: 300 characters
- **Max Content**: 40,000 characters
- **Max Media**: 20 items per post
- **Features**: Subreddit-specific posting, post types (text/link/image)

### Pinterest
- **Board Required**: Yes
- **Media Required**: Yes
- **Max Description**: 500 characters
- **Max Title**: 100 characters
- **Features**: Board management, link URLs, SEO optimization

## Error Handling

The poster system provides comprehensive error handling:

```python
result = await poster_service.post_to_platform(
    platform="unsupported_platform",
    content="This won't work"
)

if not result["success"]:
    print(f"Error: {result['error']}")
    print(f"Platform: {result['platform']}")
    print(f"Message: {result['message']}")
```

## Account Information

Get account information for connected platforms:

```python
account_info = await poster_service.get_platform_accounts_info(
    platforms=["x", "instagram", "facebook"]
)

for platform, info in account_info["accounts"].items():
    print(f"{platform}: {info['status']} - {info.get('followers', 0)} followers")
```

## Platform Requirements

Check platform-specific requirements:

```python
requirements = poster_service.get_platform_requirements("instagram")
print(f"Media required: {requirements['requirements']['media_required']}")
print(f"Max caption length: {requirements['requirements']['max_caption_length']}")
```

## Integration with Existing Services

The poster system integrates seamlessly with the existing `GetLateService`:

```python
# In your existing workflow service
from src.services.poster_service import PosterService

class WorkflowService:
    def __init__(self):
        self.getlate_service = GetLateService()
        self.poster_service = PosterService(self.getlate_service)
    
    async def post_content_workflow(self, content_data):
        # Use the new poster service instead of direct API calls
        result = await self.poster_service.post_to_platform(
            platform=content_data["platform"],
            content=content_data["content"],
            media_urls=content_data.get("media_urls"),
            **content_data.get("platform_config", {})
        )
        return result
```

## Best Practices

1. **Always validate content** before posting to avoid platform-specific errors
2. **Use platform-specific configurations** to optimize content for each platform
3. **Handle errors gracefully** - each platform has different requirements
4. **Log posting activities** for debugging and monitoring
5. **Use media URLs** that are publicly accessible
6. **Follow platform guidelines** for hashtags, mentions, and content length

## Future Enhancements

- **TikTok integration** - Video sharing platform
- **YouTube integration** - Video content posting
- **Snapchat integration** - Ephemeral content sharing
- **Advanced analytics** - Post performance tracking
- **Content scheduling** - Schedule posts for optimal times
- **A/B testing** - Test different content variations
- **AI-powered optimization** - Automatically optimize content for each platform

## Contributing

To add a new platform poster:

1. Create a new file in the `posters/` directory (e.g., `tiktok_poster.py`)
2. Inherit from `BasePoster` class
3. Implement required abstract methods
4. Register the poster in `PosterFactory`
5. Add to `__init__.py` exports
6. Update this README with platform details
7. Add usage examples to `usage_example.py`

## Troubleshooting

### Common Issues

1. **"Unsupported platform" error**
   - Check if platform name is correct
   - Ensure poster is registered in `PosterFactory`

2. **"Media required" error**
   - Some platforms (Instagram, Pinterest) require media
   - Provide valid media URLs

3. **"Content validation failed" error**
   - Check platform-specific content requirements
   - Use validation before posting

4. **API errors**
   - Ensure `GetLateService` is properly configured
   - Check API credentials and permissions

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('poster_service').setLevel(logging.DEBUG)
logging.getLogger('poster.instagram').setLevel(logging.DEBUG)
```