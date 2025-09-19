"""
Usage Example for Social Media Posters

This file demonstrates how to use the new poster system for posting to different social media platforms.
"""

import asyncio
from typing import Dict, Any, List

# Import the poster service and individual posters
from ..poster_service import PosterService
from ..getlate_service import GetLateService
from ...utils.logger_config import get_logger

async def example_single_platform_posting():
    """Example: Post to a single platform"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Content to post
    content = "🚀 Exciting news! We've just launched our new AI-powered social media automation tool. Try it out today! #AI #SocialMedia #Automation"
    
    # Media URLs (optional)
    media_urls = [
        "https://example.com/images/product-launch.jpg",
        "https://example.com/images/ai-features.png"
    ]
    
    # Post to Instagram
    result = await poster_service.post_to_platform(
        platform="instagram",
        content=content,
        media_urls=media_urls,
        hashtags=["AI", "SocialMedia", "Automation", "ProductLaunch"],
        location="San Francisco, CA"
    )
    
    print(f"Instagram posting result: {result}")
    return result

async def example_multi_platform_posting():
    """Example: Post to multiple platforms simultaneously"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Content to post
    content = "🎉 New blog post: '10 Ways AI is Revolutionizing Social Media Marketing' - Check it out and let us know what you think!"
    
    # Media URLs
    media_urls = ["https://example.com/images/ai-social-media.jpg"]
    
    # Platform-specific configurations
    platform_configs = {
        "x": {
            "hashtags": ["AI", "SocialMedia", "Marketing", "Blog"],
            "mentions": ["@YourBrand"]
        },
        "facebook": {
            "hashtags": ["ArtificialIntelligence", "SocialMediaMarketing", "DigitalMarketing"],
            "feeling": "excited"
        },
        "linkedin": {
            "hashtags": ["ArtificialIntelligence", "SocialMedia", "MarketingStrategy", "DigitalTransformation"],
            "article_url": "https://example.com/blog/ai-social-media-marketing"
        }
    }
    
    # Post to multiple platforms
    platforms = ["x", "facebook", "linkedin"]
    results = await poster_service.post_to_multiple_platforms(
        platforms=platforms,
        content=content,
        media_urls=media_urls,
        platform_configs=platform_configs
    )
    
    print(f"Multi-platform posting results: {results}")
    return results

async def example_content_validation():
    """Example: Validate content before posting"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Content to validate
    content = "This is a very long post that might exceed character limits on some platforms like X (Twitter) which has a 280 character limit. We should validate this before attempting to post to avoid errors."
    
    media_urls = ["https://example.com/image.jpg"]
    
    # Validate for multiple platforms
    platforms = ["x", "instagram", "facebook", "linkedin"]
    validation_result = await poster_service.validate_content_for_platforms(
        platforms=platforms,
        content=content,
        media_urls=media_urls
    )
    
    print(f"Content validation results: {validation_result}")
    
    # Check if content is valid for all platforms
    if validation_result["valid"]:
        print("Content is valid for all platforms!")
    else:
        print("Content has validation issues:")
        for platform, result in validation_result["platform_validations"].items():
            if not result["valid"]:
                print(f"  {platform}: {result['error']}")
    
    return validation_result

async def example_platform_specific_posting():
    """Example: Platform-specific posting with special requirements"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Reddit posting (requires subreddit)
    reddit_result = await poster_service.post_to_platform(
        platform="reddit",
        content="What are your thoughts on AI in social media marketing? Share your experiences and insights!",
        title="AI in Social Media Marketing - Discussion",
        subreddit="socialmedia",
        post_type="text"
    )
    
    # Pinterest posting (requires board_id)
    pinterest_result = await poster_service.post_to_platform(
        platform="pinterest",
        content="Beautiful AI-generated social media graphics for your marketing campaigns",
        title="AI Social Media Graphics",
        media_urls=["https://example.com/pinterest-image.jpg"],
        board_id="social-media-marketing",
        link="https://example.com/ai-graphics",
        hashtags=["AIMarketing", "SocialMedia", "Graphics"]
    )
    
    print(f"Reddit posting result: {reddit_result}")
    print(f"Pinterest posting result: {pinterest_result}")
    
    return {
        "reddit": reddit_result,
        "pinterest": pinterest_result
    }

async def example_account_info_retrieval():
    """Example: Get account information for all platforms"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Get account info for specific platforms
    platforms = ["x", "instagram", "facebook", "linkedin"]
    account_info = await poster_service.get_platform_accounts_info(platforms)
    
    print(f"Account information: {account_info}")
    
    # Get supported platforms
    supported_platforms = poster_service.get_supported_platforms()
    print(f"Supported platforms: {supported_platforms}")
    
    # Get platform requirements
    for platform in ["x", "instagram", "reddit"]:
        requirements = poster_service.get_platform_requirements(platform)
        print(f"{platform} requirements: {requirements}")
    
    return account_info

async def example_error_handling():
    """Example: Handle posting errors gracefully"""
    
    # Initialize services
    getlate_service = GetLateService()
    poster_service = PosterService(getlate_service)
    
    # Try to post to an unsupported platform
    result = await poster_service.post_to_platform(
        platform="tiktok",  # Not supported (yet)
        content="This won't work!"
    )
    
    print(f"Unsupported platform result: {result}")
    
    # Try to post without required parameters
    reddit_result = await poster_service.post_to_platform(
        platform="reddit",
        content="Missing subreddit parameter"
        # Missing required 'subreddit' parameter
    )
    
    print(f"Missing parameter result: {reddit_result}")
    
    return {
        "unsupported": result,
        "missing_param": reddit_result
    }

async def main():
    """Main function to run all examples"""
    
    print("🚀 Starting Social Media Posters Examples\n")
    
    try:
        print("1️⃣ Single Platform Posting Example:")
        await example_single_platform_posting()
        print("\n" + "="*50 + "\n")
        
        print("2️⃣ Multi-Platform Posting Example:")
        await example_multi_platform_posting()
        print("\n" + "="*50 + "\n")
        
        print("3️⃣ Content Validation Example:")
        await example_content_validation()
        print("\n" + "="*50 + "\n")
        
        print("4️⃣ Platform-Specific Posting Example:")
        await example_platform_specific_posting()
        print("\n" + "="*50 + "\n")
        
        print("5️⃣ Account Info Retrieval Example:")
        await example_account_info_retrieval()
        print("\n" + "="*50 + "\n")
        
        print("6️⃣ Error Handling Example:")
        await example_error_handling()
        print("\n" + "="*50 + "\n")
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())