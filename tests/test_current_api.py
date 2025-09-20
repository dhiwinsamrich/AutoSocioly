#!/usr/bin/env python3
"""
Test the current API implementation with enhanced image modification
"""

import requests
import json
import time
import uuid

def test_user_workflow_api():
    """Test the user workflow API with image modification"""
    print("🧪 Testing User Workflow API with Enhanced Image Modification")
    print("=" * 60)
    
    # Step 1: Create content with image
    print("\n1️⃣ Creating initial content with image...")
    
    create_data = {
        "user_input": "Modern coffee shop workspace with laptop, coffee cup, and plants for Instagram post targeting remote workers",
        "platforms": ["instagram"],
        "tone": "professional",
        "include_image": True
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/user-workflow/create-content",
            json=create_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✅ Content created successfully!")
            print(f"📝 Session ID: {session_id}")
            print(f"📊 Status: {result.get('status')}")
            print(f"💬 Message: {result.get('message')}")
            
            # Check if image was generated
            content = result.get("content", {})
            if content.get("image_url"):
                print(f"🖼️  Initial image: {content.get('image_url')[:60]}...")
            else:
                print("⚠️  No image generated in initial content")
                
        else:
            print(f"❌ Failed to create content: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating content: {e}")
        return False
    
    # Step 2: Test image modification
    print(f"\n2️⃣ Testing image modification for session {session_id}...")
    
    modify_data = {
        "session_id": session_id,
        "confirmed": False,  # Not confirming, requesting modification
        "image_modification": "Add more plants around the workspace and make the lighting warmer and more inviting",
        "regenerate_image": True,
        "regenerate_text": False
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/user-workflow/modify-content",
            json=modify_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image modification successful!")
            print(f"📝 Session ID: {result.get('session_id')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"💬 Message: {result.get('message')}")
            
            # Check the modified content
            content = result.get("content", {})
            if content.get("image_url"):
                print(f"🖼️  Modified image: {content.get('image_url')[:60]}...")
                
                # Check modification history
                history = result.get("modification_history", [])
                if history:
                    print(f"📋 Modification history entries: {len(history)}")
                    latest_mod = history[-1]
                    print(f"🔄 Latest modification: {latest_mod.get('type', 'unknown')}")
                    print(f"🕒 Modified at: {latest_mod.get('timestamp', 'unknown')}")
                
                return True
            else:
                print("❌ No modified image URL returned")
                return False
                
        else:
            print(f"❌ Image modification failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during image modification: {e}")
        return False

def test_direct_image_endpoints():
    """Test the direct image endpoints that were enhanced"""
    print("\n\n🧪 Testing Direct Image Endpoints")
    print("=" * 40)
    
    # Test the enhanced regenerate-image endpoint
    print("\n1️⃣ Testing /regenerate-image endpoint...")
    
    # First, let's create a simple workflow to test with
    test_workflow_id = str(uuid.uuid4())
    
    # Mock workflow data (this would normally be created through the content creation process)
    test_data = {
        "workflow_id": test_workflow_id,
        "prompt": "Add more plants around the workspace and make the lighting warmer and more inviting",
        "original_image_url": "https://placeholder.com/600x400/000000/FFFFFF/?text=Original+Workspace"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/regenerate-image",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Regenerate image endpoint working!")
            print(f"🎯 Success: {result.get('success', False)}")
            print(f"📸 New image URL: {result.get('image_url', 'No URL')[:60]}...")
            print(f"🔄 Original preserved: {result.get('original_image_url', 'N/A')[:60]}...")
            print(f"💬 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Regenerate image endpoint failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing regenerate image: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Enhanced Image Modification Tests")
    print("=" * 60)
    
    # Test 1: User Workflow API
    user_workflow_success = test_user_workflow_api()
    
    # Test 2: Direct Image Endpoints  
    direct_endpoints_success = test_direct_image_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"User Workflow API: {'✅ PASS' if user_workflow_success else '❌ FAIL'}")
    print(f"Direct Image Endpoints: {'✅ PASS' if direct_endpoints_success else '❌ FAIL'}")
    
    if user_workflow_success and direct_endpoints_success:
        print("\n🎉 All tests passed! Enhanced image modification is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)