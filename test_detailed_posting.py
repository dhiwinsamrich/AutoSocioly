#!/usr/bin/env python3
"""
Detailed test to see exactly what's being sent to GetLate API
"""

import asyncio
import sys
import os
import json
from pathlib import Path
import logging

# Set up logging to see everything
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.user_workflow_service import UserWorkflowService
from src.services.getlate_service import GetLateService
from src.services.poster_service import PosterService
from src.config import settings

async def test_detailed_posting():
    """Test with detailed logging to see exactly what's happening"""
    
    print("=== Detailed Instagram Posting Test ===")
    
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
        content_package = result["content"]
        
        print(f"✅ User input processed successfully")
        print(f"   Session ID: {session_id}")
        print(f"   Public images: {len(content_package.get('public_images', []))}")
        
        if content_package.get('public_images'):
            for i, img in enumerate(content_package['public_images']):
                print(f"   Image {i+1}: {img.get('public_url')} (accessible: {img.get('accessible')})")
        
        # Now let's manually test the posting process
        print("\n3. Manual posting test...")
        
        # Get the platform content
        platform = "instagram"
        platform_content = content_package["platform_content"][platform]
        
        # Prepare content (same as in the service)
        post_content = f"{platform_content['caption']}\n\n"
        post_content += " ".join([f"#{tag}" for tag in platform_content['hashtags']])
        
        # Get media URLs
        media_urls = []
        if content_package.get("public_images"):
            media_urls = [img.get("public_url") for img in content_package["public_images"]]
        
        print(f"   Content: {post_content[:100]}...")
        print(f"   Media URLs: {media_urls}")
        
        # Test the GetLate service directly
        print("\n4. Testing GetLate service directly...")
        getlate_service = GetLateService(api_key=settings.GETLATE_API_KEY)
        
        try:
            result = getlate_service.post_to_instagram(post_content, media_urls)
            print(f"   GetLate result: {result}")
            return True
            
        except Exception as e:
            print(f"   ❌ GetLate service failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error in detailed test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_detailed_posting())
    print(f"\n=== Final Result ===")
    print(f"Detailed posting test: {'SUCCESS' if result else 'FAILED'}")