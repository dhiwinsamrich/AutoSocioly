# 🔐 Authentication Implementation Guide

## Overview
This guide demonstrates the proper authentication implementation for all social media platforms using the GetLate API with Bearer token authentication and ngrok integration for public image URLs.

## ✅ Authentication Updates Completed

### 1. Bearer Token Authentication
- **Updated**: `src/services/getlate_service.py`
- **Change**: Authorization header now uses `Bearer {api_key}` format
- **Before**: `Authorization: sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28`
- **After**: `Authorization: Bearer sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28`

### 2. Platform-Specific Authentication Service
- **Created**: `src/services/auth_service.py`
- **Features**:
  - Platform-specific authentication configurations
  - Account ID management for each platform
  - Media URL generation with ngrok integration
  - Validation and error handling
  - Batch posting support

### 3. Complete Platform Support

#### 🔴 Reddit Authentication
```json
{
  "content": "Discussion thread for our latest article",
  "platforms": [{
    "platform": "reddit",
    "accountId": "REDDIT_ACCOUNT_ID",
    "platformSpecificData": {
      "subreddit": "reactjs",
      "url": "https://example.com/article"
    }
  }]
}
```

#### 📸 Instagram Authentication
```json
{
  "content": "Check out our latest AI technology innovation! 🚀",
  "platforms": [{
    "platform": "instagram",
    "accountId": "INSTAGRAM_ACCOUNT_ID",
    "platformSpecificData": {
      "caption": "Amazing AI technology trends for 2024! #AI #Technology #Innovation",
      "hashtags": ["#AI", "#Technology", "#Innovation"]
    }
  }],
  "media_items": [{
    "type": "image",
    "url": "https://43d3dda256d5.ngrok-free.app/static/images/ai-technology.jpg"
  }]
}
```

#### 💼 LinkedIn Authentication
```json
{
  "content": "Excited to share insights about AI technology trends",
  "platforms": [{
    "platform": "linkedin",
    "accountId": "LINKEDIN_ACCOUNT_ID",
    "platformSpecificData": {
      "visibility": "public",
      "article_url": "https://example.com/article"
    }
  }]
}
```

#### 🐦 X (Twitter) Authentication
```json
{
  "content": "🚀 AI technology is revolutionizing how we work and live!",
  "platforms": [{
    "platform": "x",
    "accountId": "X_ACCOUNT_ID",
    "platformSpecificData": {
      "hashtags": ["#AI", "#Technology", "#Innovation"],
      "mentions": ["@techhandle"]
    }
  }]
}
```

#### 🔵 Facebook Authentication
```json
{
  "content": "Discover the latest AI technology trends that are shaping our future! 🌟",
  "platforms": [{
    "platform": "facebook",
    "accountId": "FACEBOOK_ACCOUNT_ID",
    "platformSpecificData": {
      "privacy": "public",
      "link": "https://example.com/article"
    }
  }]
}
```

#### 📌 Pinterest Authentication
```json
{
  "content": "Amazing AI technology trends and innovations",
  "platforms": [{
    "platform": "pinterest",
    "accountId": "PINTEREST_ACCOUNT_ID",
    "platformSpecificData": {
      "board": "technology",
      "description": "Discover cutting-edge AI technology trends",
      "link": "https://example.com/article"
    }
  }],
  "media_items": [{
    "type": "image",
    "url": "https://43d3dda256d5.ngrok-free.app/static/images/ai-technology-pin.jpg"
  }]
}
```

#### 🎵 TikTok Authentication
```json
{
  "content": "Check out this amazing AI technology demo! 🚀",
  "platforms": [{
    "platform": "tiktok",
    "accountId": "TIKTOK_ACCOUNT_ID",
    "platformSpecificData": {
      "description": "Amazing AI technology in action! #AI #Technology #Innovation",
      "hashtags": ["#AI", "#Technology", "#Innovation"]
    }
  }],
  "media_items": [{
    "type": "video",
    "url": "https://43d3dda256d5.ngrok-free.app/static/videos/ai-technology-demo.mp4"
  }]
}
```

#### 📺 YouTube Authentication
```json
{
  "content": "Comprehensive guide to AI technology trends for 2024",
  "platforms": [{
    "platform": "youtube",
    "accountId": "YOUTUBE_ACCOUNT_ID",
    "platformSpecificData": {
      "title": "AI Technology Trends 2024 - Complete Guide",
      "description": "Discover the latest AI technology trends",
      "tags": ["AI", "Technology", "Innovation", "2024"],
      "category": "Science & Technology"
    }
  }],
  "media_items": [{
    "type": "video",
    "url": "https://43d3dda256d5.ngrok-free.app/static/videos/ai-technology-guide.mp4"
  }]
}
```

## 🌐 Ngrok Integration

### Setup
```bash
# Install ngrok
pip install ngrok

# Start ngrok tunnel (automatically handled by AuthService)
# The service will automatically create tunnels for local images
```

### Usage
```python
from src.services.auth_service import AuthService
from src.services.getlate_service import GetLateService

# Initialize services
getlate_service = GetLateService(api_key="your_api_key")
auth_service = AuthService(getlate_service)

# Make local images public
image_paths = ["static/uploads/my-image.jpg"]
public_urls = auth_service.make_public_media_urls(image_paths)
# Returns: ["https://43d3dda256d5.ngrok-free.app/static/images/my-image.jpg"]
```

## 🚀 Complete Workflow Example

### 1. Create Content Workflow
```bash
curl -X POST http://localhost:8000/create-content \
  -F "topic=AI Technology Trends 2024" \
  -F "platforms=instagram,linkedin,x,reddit" \
  -F "tone=professional"
```

### 2. Generate Images (if needed)
```bash
curl -X POST http://localhost:8000/regenerate-image \
  -F "workflow_id=YOUR_WORKFLOW_ID" \
  -F "prompt=AI technology trends 2024 professional banner"
```

### 3. Publish to Platforms
```bash
curl -X POST http://localhost:8000/publish-content \
  -F "workflow_id=YOUR_WORKFLOW_ID" \
  -F "selected_variants[instagram]=Check out our AI tech trends! #AI #Technology" \
  -F "selected_variants[linkedin]=AI technology insights for 2024" \
  -F "selected_variants[x]=🚀 AI trends shaping 2024! #AI #Tech" \
  -F "selected_variants[reddit]=Discussion: AI Technology Trends 2024"
```

### 4. Batch Post via GetLate API
```python
import requests

api_key = "sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28"

post_data = {
    "content": "AI Technology Trends 2024: Latest innovations! 🚀",
    "platforms": [
        {
            "platform": "instagram",
            "accountId": "instagram_account",
            "platformSpecificData": {
                "hashtags": ["#AI", "#Technology", "#2024"],
                "caption": "Amazing AI technology trends!"
            }
        },
        {
            "platform": "linkedin",
            "accountId": "linkedin_account",
            "platformSpecificData": {
                "visibility": "public"
            }
        }
    ],
    "media_items": [{
        "type": "image",
        "url": "https://43d3dda256d5.ngrok-free.app/static/images/ai-trends.jpg"
    }]
}

response = requests.post(
    'https://getlate.dev/api/v1/posts',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json=post_data
)
```

## 📋 Platform Requirements

| Platform | Account ID | Media Required | Special Fields |
|----------|------------|----------------|----------------|
| Reddit | ✅ | ❌ | subreddit, url |
| Instagram | ✅ | ✅ | hashtags, caption, location |
| LinkedIn | ✅ | ❌ | visibility, article_url |
| X (Twitter) | ✅ | ❌ | hashtags, mentions |
| Facebook | ✅ | ❌ | privacy, link |
| Pinterest | ✅ | ✅ | board, description, link |
| TikTok | ✅ | ✅ | description, hashtags |
| YouTube | ✅ | ✅ | title, description, tags, category |

## 🔧 Testing Scripts

### Quick Authentication Test
```bash
python platform_auth_examples.py
```

### Complete Integration Test
```bash
python complete_platform_integration.py
```

### Manual cURL Testing
```bash
# Reddit
curl -X POST 'https://getlate.dev/api/v1/posts' \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test Reddit post",
    "platforms": [{
      "platform": "reddit",
      "accountId": "YOUR_REDDIT_ACCOUNT",
      "platformSpecificData": {"subreddit": "technology"}
    }]
  }'
```

## 🎯 Key Features Implemented

1. **Bearer Token Authentication**: All API requests now use proper Bearer token format
2. **Platform-Specific Configurations**: Each platform has its own authentication requirements
3. **Media URL Management**: ngrok integration for public image URLs
4. **Batch Posting Support**: Post to multiple platforms simultaneously
5. **Validation & Error Handling**: Comprehensive validation for each platform
6. **Account ID Management**: Proper account mapping for each platform
7. **Complete Platform Coverage**: Support for all major social media platforms

## 🚀 Next Steps

1. **Configure Your Account IDs**: Replace demo account IDs with your actual account IDs
2. **Set Up ngrok**: Install ngrok for image tunneling if needed
3. **Test Individual Platforms**: Start with one platform and expand
4. **Customize Content**: Tailor content for each platform's audience
5. **Monitor Performance**: Track posting success rates and engagement

## 📞 Support

For issues with authentication:
1. Check your API key is valid and has proper permissions
2. Verify account IDs are correct for each platform
3. Ensure media URLs are publicly accessible (use ngrok for local images)
4. Review platform-specific requirements in the validation output
5. Check the GetLate API documentation for any platform-specific changes

---

**✅ Authentication implementation complete! All platforms now support proper Bearer token authentication with platform-specific configurations.**