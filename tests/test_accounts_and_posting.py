#!/usr/bin/env python3
"""Test GetLate API accounts and posting with detailed error analysis"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.getlate_service import GetLateService
from src.models import GetLatePostData
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_accounts_and_posting():
    """Test accounts connectivity and posting with detailed analysis"""
    
    # Get API key from environment
    api_key = os.getenv('GETLATE_API_KEY', 'sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28')
    
    # Initialize service
    service = GetLateService(api_key=api_key)
    
    try:
        print("=== Step 1: Testing Account Connectivity ===")
        print("Fetching connected accounts...")
        
        accounts = service.get_accounts()
        print(f"✅ Successfully retrieved {len(accounts)} accounts")
        
        for account in accounts:
            print(f"  - Platform: {account.platform}, Username: {account.username}, Connected: {account.connected}")
        
        print("\n=== Step 2: Testing Different Platforms ===")
        
        # Test platforms that might be available
        platforms_to_test = ['linkedin', 'x', 'facebook', 'instagram']
        
        for platform in platforms_to_test:
            print(f"\n--- Testing {platform.upper()} ---")
            
            post_data = GetLatePostData(
                content=f"Testing {platform} posting with fixed endpoint",
                platforms=[{"platform": platform}]
            )
            
            try:
                result = service.create_post(post_data)
                print(f"✅ {platform.upper()}: SUCCESS - Post created: {result.get('id')}")
                break  # Stop if we find a working platform
                
            except Exception as e:
                error_msg = str(e)
                status_code = getattr(e, 'status_code', 'unknown')
                print(f"❌ {platform.upper()}: FAILED - Status: {status_code}, Error: {error_msg}")
                
                # If it's a 500 error, try with different content or media
                if status_code == 500:
                    print(f"  → Retrying {platform} with different content...")
                    try:
                        # Try with simpler content
                        simple_post = GetLatePostData(
                            content=f"Simple test post for {platform}",
                            platforms=[{"platform": platform}]
                        )
                        result = service.create_post(simple_post)
                        print(f"✅ {platform.upper()}: SUCCESS on retry - Post created: {result.get('id')}")
                        break
                    except Exception as e2:
                        print(f"  → Retry failed: {str(e2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Account test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"Message: {e.message}")
        return False

if __name__ == "__main__":
    success = test_accounts_and_posting()
    if success:
        print("\n🎉 Account connectivity and posting test completed!")
    else:
        print("\n❌ Account connectivity and posting test failed.")