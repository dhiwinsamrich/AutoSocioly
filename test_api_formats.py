#!/usr/bin/env python3
"""
Test different API formats to see what GetLate expects
"""

import asyncio
import sys
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.getlate_service import GetLateService
from src.config import settings

async def test_api_formats():
    """Test different API formats"""
    
    print("=== Testing GetLate API Formats ===")
    
    getlate_service = GetLateService(api_key=settings.GETLATE_API_KEY)
    
    # Test different formats
    test_formats = [
        {
            "name": "Current format",
            "data": {
                "content": "Test post with image",
                "platforms": [{"platform": "instagram"}],
                "media_items": [{"type": "image", "url": "https://example.com/test.jpg"}]
            }
        },
        {
            "name": "Simple format",
            "data": {
                "content": "Test post with image",
                "platforms": ["instagram"],
                "media_items": [{"type": "image", "url": "https://example.com/test.jpg"}]
            }
        },
        {
            "name": "Without media_items",
            "data": {
                "content": "Test post without image",
                "platforms": [{"platform": "instagram"}]
            }
        },
        {
            "name": "Text only",
            "data": {
                "content": "Test post text only",
                "platforms": ["instagram"]
            }
        }
    ]
    
    for test in test_formats:
        print(f"\n--- Testing: {test['name']} ---")
        try:
            # Create the post data
            from src.models import GetLatePostData
            post_data = GetLatePostData(**test['data'])
            
            # Log what we're sending
            request_data = post_data.dict(exclude_none=True)
            print(f"Sending: {json.dumps(request_data, indent=2)}")
            
            # Try to create the post
            result = getlate_service.create_post(post_data)
            print(f"✅ Success: {result}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            # Check if it's a 405 error (method not allowed)
            if hasattr(e, 'status_code') and e.status_code == 405:
                print("📝 This is a 405 error - the API endpoint might not support this method")
            elif hasattr(e, 'status_code') and e.status_code == 400:
                print("📝 This is a 400 error - the request format might be wrong")
                if hasattr(e, 'response_data'):
                    print(f"Response data: {e.response_data}")

if __name__ == "__main__":
    asyncio.run(test_api_formats())