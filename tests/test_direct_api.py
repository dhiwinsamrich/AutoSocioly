#!/usr/bin/env python3
"""Direct test of GetLate API to verify the endpoint fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.getlate_service import GetLateService
from src.models import GetLatePostData
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_direct_api():
    """Test the GetLate API directly"""
    
    # Get API key from environment
    api_key = os.getenv('GETLATE_API_KEY', 'your-api-key-here')
    
    # Initialize service
    service = GetLateService(api_key=api_key)
    
    # Test data
    post_data = GetLatePostData(
        content="Testing the fixed endpoint for LinkedIn posting",
        platforms=[{"platform": "linkedin"}]
    )
    
    try:
        print("Testing direct API call to GetLate service...")
        print(f"Using endpoint: /v1/posts")
        print(f"Post data: {post_data.dict()}")
        
        result = service.create_post(post_data)
        
        print(f"✅ SUCCESS: API call successful!")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: API call failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"Message: {e.message}")
        return False

if __name__ == "__main__":
    success = test_direct_api()
    if success:
        print("\n🎉 Direct API test passed!")
    else:
        print("\n❌ Direct API test failed.")