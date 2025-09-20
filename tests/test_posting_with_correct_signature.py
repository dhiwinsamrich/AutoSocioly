#!/usr/bin/env python3
"""Test posting to connected platforms using the correct method signature"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.getlate_service import GetLateService, GetLatePostData
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_posting_with_correct_signature():
    """Test posting to each connected platform using correct GetLatePostData"""
    
    # Get API key from environment
    api_key = os.getenv('GETLATE_API_KEY', 'sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28')
    
    # Initialize service
    service = GetLateService(api_key=api_key)
    
    # Get connected accounts
    try:
        accounts = service.get_accounts()
        connected_platforms = [acc.platform for acc in accounts if acc.connected]
        print(f"Connected platforms: {connected_platforms}")
    except Exception as e:
        print(f"Failed to get accounts: {e}")
        return False
    
    # Test posting to each connected platform
    test_results = []
    
    for platform in connected_platforms:
        print(f"\n{'='*50}")
        print(f"Testing {platform.value.upper()}")
        print(f"{'='*50}")
        
        try:
            # Create GetLatePostData object
            content = f"Test post to {platform.value} using fixed endpoint /v1/posts"
            platforms = [{"platform": platform.value}]
            
            post_data = GetLatePostData(
                content=content,
                platforms=platforms
            )
            
            print(f"Content: {content}")
            print(f"Platforms: {platforms}")
            print(f"Post data object created successfully")
            
            # Try to create the post
            result = service.create_post(post_data)
            
            print(f"✅ SUCCESS: Post created successfully")
            print(f"Result: {result}")
            test_results.append({
                'platform': platform.value,
                'success': True,
                'result': result
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
            if hasattr(e, 'message'):
                print(f"Message: {e.message}")
            
            test_results.append({
                'platform': platform.value,
                'success': False,
                'error': str(e),
                'status_code': getattr(e, 'status_code', None)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for r in test_results if r['success'])
    total = len(test_results)
    
    print(f"Total platforms tested: {total}")
    print(f"Successful posts: {successful}")
    print(f"Failed posts: {total - successful}")
    
    for result in test_results:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{result['platform']}: {status}")
        if not result['success'] and result.get('status_code'):
            print(f"  → Status: {result['status_code']}, Error: {result['error']}")
    
    return successful > 0

if __name__ == "__main__":
    success = test_posting_with_correct_signature()
    if success:
        print("\n🎉 At least one platform accepted the post!")
    else:
        print("\n❌ All platforms rejected the posts.")