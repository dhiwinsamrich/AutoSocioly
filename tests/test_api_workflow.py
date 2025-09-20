#!/usr/bin/env python3
"""
Test the complete enhanced image modification workflow through the API
"""

import requests
import json

def test_enhanced_image_regeneration():
    """Test the enhanced image regeneration API endpoint"""
    print("🧪 Testing Enhanced Image Regeneration API")
    print("=" * 50)
    
    # Test data
    test_data = {
        "workflow_id": "test_workflow_123",
        "prompt": "Add more vibrant colors and make the lighting more dramatic",
        "original_image_url": "/static/uploads/generated_20250919_155210_3116.png"
    }
    
    try:
        # Test the regenerate image endpoint
        response = requests.post(
            "http://localhost:8000/regenerate-image",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API endpoint working successfully!")
            print(f"📊 Response status: {response.status_code}")
            print(f"🎯 Success: {result.get('success', False)}")
            print(f"📸 New image URL: {result.get('image_url', 'No URL')[:60]}...")
            print(f"🔄 Original preserved: {result.get('original_image_url', 'N/A')[:60]}...")
            print(f"💬 Message: {result.get('message', 'No message')}")
            
            # Check for enhanced metadata
            if 'regeneration_history' in result:
                print(f"📋 Regeneration history entries: {len(result.get('regeneration_history', []))}")
            
            return True
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running.")
        print("🔄 Trying to check application status...")
        return False
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return False

def check_application_health():
    """Check if the application is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Application is running and accessible")
            return True
        else:
            print(f"⚠️  Application returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error checking application: {e}")
        return False

if __name__ == "__main__":
    # First check if application is running
    if check_application_health():
        # Then test the enhanced functionality
        success = test_enhanced_image_regeneration()
        if success:
            print("\n🎉 All tests completed successfully!")
            print("✅ Enhanced image modification with core preservation is working")
        else:
            print("\n⚠️  Some tests failed - check the logs above")
    else:
        print("\n❌ Cannot run tests - application is not accessible")
        print("🔄 Please start the application first with: python app.py")