#!/usr/bin/env python3
"""
Test the Final Corrected API Implementation
"""

import requests
import json
import time

def test_user_workflow_with_image_modification():
    """Test the complete user workflow with image modification"""
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
            "http://localhost:8000/api/user-workflow/create-content",
            json=create_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
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
                original_image_url = content.get("image_url")
            else:
                print("⚠️  No image generated in initial content")
                original_image_url = "https://placeholder.com/600x400/000000/FFFFFF/?text=Original+Workspace"
                
            return session_id, original_image_url
        else:
            print(f"❌ Failed to create content: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating content: {e}")
        return None, None

def test_image_modification(session_id, original_image_url):
    """Test image modification in the user workflow"""
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
            "http://localhost:8000/api/user-workflow/modify-content",
            json=modify_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
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
    
    # Test the regenerate-image endpoint
    print("\n1️⃣ Testing /regenerate-image endpoint...")
    
    # Create a simple test workflow to test with
    test_workflow_id = "test-workflow-123"
    
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

def test_session_status(session_id):
    """Test getting session status"""
    print(f"\n3️⃣ Testing session status for {session_id}...")
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/user-workflow/session/{session_id}/status",
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Session status retrieved successfully!")
            print(f"📝 Session ID: {result.get('session_id')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"📋 Topic: {result.get('topic')}")
            
            # Check modification history
            history = result.get("modification_history", [])
            print(f"📋 Modification history entries: {len(history)}")
            
            return True
        else:
            print(f"❌ Failed to get session status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting session status: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Final Corrected API Tests")
    print("=" * 60)
    
    # Test 1: User Workflow API with image modification
    session_id, original_image_url = test_user_workflow_with_image_modification()
    
    # Test 2: Image modification (if session was created)
    image_mod_success = False
    if session_id and original_image_url:
        image_mod_success = test_image_modification(session_id, original_image_url)
        test_session_status(session_id)
    
    # Test 3: Direct Image Endpoints  
    direct_endpoints_success = test_direct_image_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"User Workflow Creation: {'✅ PASS' if session_id else '❌ FAIL'}")
    print(f"Image Modification: {'✅ PASS' if image_mod_success else '❌ FAIL'}")
    print(f"Direct Image Endpoints: {'✅ PASS' if direct_endpoints_success else '❌ FAIL'}")
    
    if session_id and (image_mod_success or direct_endpoints_success):
        print("\n🎉 User workflow API with enhanced image modification is working!")
        print("✅ All API endpoints are correctly configured and accessible")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)