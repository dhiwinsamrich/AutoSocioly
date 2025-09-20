#!/usr/bin/env python3
"""
Test actual Instagram posting to see what's happening with the image URL parameter
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.user_workflow_service import UserWorkflowService
from src.services.getlate_service import GetLateService
from src.services.poster_service import PosterService
from src.services.image_gen import ImageGenerationService
from src.services.text_gen import TextGenerationService
from src.utils.ngrok_manager import NgrokManager

async def test_actual_posting():
    """Test the actual posting process to see what parameters are being sent"""
    
    print("=== Testing Actual Instagram Posting ===")
    
    try:
        # Initialize services
        print("1. Initializing services...")
        workflow_service = UserWorkflowService()
        
        # Process user input
        print("2. Processing user input...")
        result = await workflow_service.process_user_input(
            user_input="Beautiful sunset photography tips",
            platforms=["instagram"],
            tone="engaging",
            include_image=True
        )
        
        if not result.get("success"):
            print(f"❌ Failed to process user input: {result.get('error')}")
            return False
            
        session_id = result["session_id"]
        print(f"✅ User input processed successfully")
        print(f"   Session ID: {session_id}")
        print(f"   Public images: {len(result['content'].get('public_images', []))}")
        
        # Get the content package
        content_package = result["content"]
        public_images = content_package.get("public_images", [])
        
        if public_images:
            print(f"   First image URL: {public_images[0].get('public_url')}")
            print(f"   First image accessible: {public_images[0].get('accessible')}")
        
        # Now let's test what happens when we try to post
        print("\n3. Testing content posting...")
        
        # Extract the posting logic to see what's happening
        platform = "instagram"
        platform_content = content_package["platform_content"][platform]
        
        # Prepare content for posting (same as in the service)
        post_content = f"{platform_content['caption']}\n\n"
        post_content += " ".join([f"#{tag}" for tag in platform_content['hashtags']])
        
        # Add image if available (same as in the service)
        media_urls = []
        if content_package.get("public_images"):
            media_urls = [img.get("public_url") for img in content_package["public_images"]]
        
        print(f"   Platform: {platform}")
        print(f"   Content length: {len(post_content)} characters")
        print(f"   Media URLs count: {len(media_urls)}")
        if media_urls:
            print(f"   First media URL: {media_urls[0]}")
        
        # Test the poster service directly
        print("\n4. Testing poster service directly...")
        from src.config import settings
        getlate_service = GetLateService(api_key=settings.GETLATE_API_KEY)
        poster_service = PosterService(getlate_service)
        
        poster = poster_service.get_poster(platform)
        print(f"   Poster type: {type(poster).__name__}")
        
        # Try to post and see what happens
        try:
            result = await poster.post_content(
                content=post_content,
                media_urls=media_urls
            )
            
            print(f"   Posting result: {result}")
            
            if result.get("success"):
                print("✅ Posting successful!")
                return True
            else:
                print(f"❌ Posting failed: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during posting: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error in posting test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_actual_posting())
    print(f"\n=== Final Result ===")
    print(f"Actual posting test: {'SUCCESS' if result else 'FAILED'}")