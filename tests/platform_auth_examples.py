#!/usr/bin/env python3
"""
Platform Authentication Examples - Demonstrates proper authentication for all social media platforms
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import our services
from src.services.getlate_service import GetLateService
from src.services.auth_service import AuthService
from src.models import Platform

def get_api_key() -> str:
    """Get API key from environment"""
    return os.getenv('GETLATE_API_KEY', 'sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28')

def create_example_curl_commands():
    """Generate example cURL commands for all platforms"""
    api_key = get_api_key()
    base_url = "https://getlate.dev/api/v1"
    
    print("🚀 PLATFORM AUTHENTICATION EXAMPLES")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Reddit Example
    print("\n🔴 REDDIT AUTHENTICATION EXAMPLE")
    print("-" * 40)
    reddit_data = {
        "content": "Discussion thread for our latest article about AI technology trends",
        "platforms": [{
            "platform": "reddit",
            "accountId": "REDDIT_ACCOUNT_ID",
            "platformSpecificData": {
                "subreddit": "reactjs",
                "url": "https://example.com/article"
            }
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(reddit_data, indent=2)}'""")
    
    # Instagram Example
    print("\n📸 INSTAGRAM AUTHENTICATION EXAMPLE")
    print("-" * 40)
    instagram_data = {
        "content": "Check out our latest AI technology innovation! 🚀",
        "platforms": [{
            "platform": "instagram",
            "accountId": "INSTAGRAM_ACCOUNT_ID",
            "platformSpecificData": {
                "caption": "Amazing AI technology trends for 2024! #AI #Technology #Innovation",
                "hashtags": ["#AI", "#Technology", "#Innovation", "#Future"]
            }
        }],
        "media_items": [{
            "type": "image",
            "url": "https://example.com/ai-technology-image.jpg"
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(instagram_data, indent=2)}'""")
    
    # LinkedIn Example
    print("\n💼 LINKEDIN AUTHENTICATION EXAMPLE")
    print("-" * 40)
    linkedin_data = {
        "content": "Excited to share insights about AI technology trends shaping 2024 and beyond.",
        "platforms": [{
            "platform": "linkedin",
            "accountId": "LINKEDIN_ACCOUNT_ID",
            "platformSpecificData": {
                "visibility": "public",
                "article_url": "https://example.com/article"
            }
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(linkedin_data, indent=2)}'""")
    
    # X (Twitter) Example
    print("\n🐦 X (TWITTER) AUTHENTICATION EXAMPLE")
    print("-" * 40)
    x_data = {
        "content": "🚀 AI technology is revolutionizing how we work and live! Check out the latest trends.",
        "platforms": [{
            "platform": "x",
            "accountId": "X_ACCOUNT_ID",
            "platformSpecificData": {
                "hashtags": ["#AI", "#Technology", "#Innovation"],
                "mentions": ["@techhandle"]
            }
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(x_data, indent=2)}'""")
    
    # Facebook Example
    print("\n🔵 FACEBOOK AUTHENTICATION EXAMPLE")
    print("-" * 40)
    facebook_data = {
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
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(facebook_data, indent=2)}'""")
    
    # Pinterest Example
    print("\n📌 PINTEREST AUTHENTICATION EXAMPLE")
    print("-" * 40)
    pinterest_data = {
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
            "url": "https://example.com/ai-technology-pin.jpg"
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(pinterest_data, indent=2)}'""")
    
    # TikTok Example
    print("\n🎵 TIKTOK AUTHENTICATION EXAMPLE")
    print("-" * 40)
    tiktok_data = {
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
            "url": "https://example.com/ai-technology-demo.mp4"
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(tiktok_data, indent=2)}'""")
    
    # YouTube Example
    print("\n📺 YOUTUBE AUTHENTICATION EXAMPLE")
    print("-" * 40)
    youtube_data = {
        "content": "Comprehensive guide to AI technology trends for 2024",
        "platforms": [{
            "platform": "youtube",
            "accountId": "YOUTUBE_ACCOUNT_ID",
            "platformSpecificData": {
                "title": "AI Technology Trends 2024 - Complete Guide",
                "description": "Discover the latest AI technology trends that are reshaping our world in 2024",
                "tags": ["AI", "Technology", "Innovation", "2024"],
                "category": "Science & Technology"
            }
        }],
        "media_items": [{
            "type": "video",
            "url": "https://example.com/ai-technology-guide.mp4"
        }]
    }
    print(f"""curl -X POST '{base_url}/posts' \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(youtube_data, indent=2)}'""")

def test_authentication_service():
    """Test the authentication service with proper formatting"""
    print("\n\n🔧 TESTING AUTHENTICATION SERVICE")
    print("=" * 60)
    
    # Initialize services
    api_key = get_api_key()
    getlate_service = GetLateService(api_key=api_key)
    auth_service = AuthService(getlate_service)
    
    # Test platform configurations
    platforms = [Platform.REDDIT, Platform.INSTAGRAM, Platform.LINKEDIN, Platform.X]
    
    print("\n📋 Platform Authentication Configurations:")
    for platform in platforms:
        config = auth_service.get_platform_auth_config(platform)
        print(f"\n{platform.value.title()}:")
        print(f"  - Auth Type: {config.get('auth_type', 'unknown')}")
        print(f"  - Endpoint: {config.get('endpoint', 'unknown')}")
        print(f"  - Requires Account ID: {config.get('requires_account_id', False)}")
        print(f"  - Requires Media: {config.get('requires_media', False)}")
    
    # Test post data creation
    print("\n\n📝 Testing Post Data Creation:")
    content = "Amazing AI technology trends for 2024! 🚀"
    account_mappings = {
        Platform.REDDIT: "reddit_test_account",
        Platform.INSTAGRAM: "instagram_test_account",
        Platform.LINKEDIN: "linkedin_test_account",
        Platform.X: "x_test_account"
    }
    
    platform_configs = {
        Platform.REDDIT: {"subreddit": "technology", "url": "https://example.com/ai-trends"},
        Platform.INSTAGRAM: {"hashtags": ["#AI", "#Technology", "#2024"]},
        Platform.LINKEDIN: {"visibility": "public", "article_url": "https://example.com/ai-trends"},
        Platform.X: {"hashtags": ["#AI", "#Tech"], "mentions": ["@technews"]}
    }
    
    post_data = auth_service.create_authenticated_post_data(
        content=content,
        platforms=platforms,
        account_mappings=account_mappings,
        platform_configs=platform_configs
    )
    
    print(f"\nGenerated Post Data:")
    print(json.dumps(post_data, indent=2))
    
    # Test validation
    print("\n\n✅ Testing Platform Validation:")
    for platform in platforms:
        validation = auth_service.validate_platform_requirements(
            platform=platform,
            content=content,
            media_urls=["https://example.com/image.jpg"] if platform in [Platform.INSTAGRAM] else None,
            platform_config=platform_configs.get(platform)
        )
        print(f"\n{platform.value.title()} Validation:")
        print(f"  - Valid: {validation['valid']}")
        if validation.get('errors'):
            print(f"  - Errors: {validation['errors']}")
        if validation.get('warnings'):
            print(f"  - Warnings: {validation['warnings']}")

def test_ngrok_integration():
    """Test ngrok integration for making images public"""
    print("\n\n🌐 TESTING NGROK INTEGRATION")
    print("=" * 60)
    
    # Initialize services
    api_key = get_api_key()
    getlate_service = GetLateService(api_key=api_key)
    auth_service = AuthService(getlate_service)
    
    # Test with a sample image (create if doesn't exist)
    sample_image_path = "static/uploads/sample_test_image.jpg"
    
    # Create a dummy image file for testing
    if not Path(sample_image_path).exists():
        # Create a simple test image (1x1 pixel black image)
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='black')
            img.save(sample_image_path)
            print(f"✅ Created test image: {sample_image_path}")
        except ImportError:
            print("❌ PIL not available, creating placeholder file")
            Path(sample_image_path).touch()
    
    # Test making image public
    print(f"\n📸 Testing public URL creation for: {sample_image_path}")
    public_urls = auth_service.make_public_media_urls([sample_image_path])
    
    if public_urls:
        print(f"✅ Public URL created: {public_urls[0]}")
        print("\n📋 You can now use this URL in your social media posts!")
    else:
        print("❌ Failed to create public URL")
        print("💡 Make sure ngrok is installed and running")

if __name__ == "__main__":
    # Run all examples
    create_example_curl_commands()
    test_authentication_service()
    test_ngrok_integration()
    
    print("\n\n🎉 AUTHENTICATION EXAMPLES COMPLETE!")
    print("=" * 60)
    print("\n💡 Key Takeaways:")
    print("  - Use Bearer token authentication with your API key")
    print("  - Each platform requires specific account ID and configuration")
    print("  - Media platforms (Instagram, Pinterest, TikTok, YouTube) require image/video URLs")
    print("  - Use ngrok to make local images publicly accessible")
    print("  - Platform-specific data should be included in platformSpecificData field")
    print("\n🔧 Next Steps:")
    print("  1. Set up your account IDs for each platform")
    print("  2. Install ngrok for image tunneling: pip install ngrok")
    print("  3. Test with your actual API key and account IDs")
    print("  4. Use the AuthService class for programmatic access")