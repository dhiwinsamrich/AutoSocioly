#!/usr/bin/env python3
"""
Test the corrected API implementation
"""

import requests
import json
import time
import uuid

def test_create_content():
    """Test the create-content endpoint"""
    print("🧪 Testing Create Content API")
    print("=" * 40)
    
    # Step 1: Create content with image
    print("\n1️⃣ Creating initial content with image...")
    
    form_data = {
        "topic": "Modern coffee shop workspace with laptop, coffee cup, and plants for Instagram post targeting remote workers",
        "platforms": ["instagram"],
        "tone": "professional",
        "include_image": True,
        "caption_length": "medium",
        "hashtag_count": 10
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/create-content",
            data=form_data,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # This returns HTML, so we need to extract the workflow_id from the response
            html_content = response.text
            print("✅ Content creation request successful!")
            print(f"📄 Response length: {len(html_content)} characters")
            
            # Look for workflow_id in the HTML response
            if 'workflow_id' in html_content:
                print("📝 Workflow ID found in HTML response")
                # Extract workflow_id from HTML (this is a simple approach)
                import re
                workflow_match = re.search(r'workflow_id\s*=\s*["\']([^"\']+)["\']', html_content)
                if workflow_match:
                    workflow_id = workflow_match.group(1)
                    print(f"🎯 Extracted Workflow ID: {workflow_id}")
                    return workflow_id
                else:
                    print("⚠️  Could not extract workflow_id from HTML")
                    return None
            else:
                print("⚠️  No workflow_id found in HTML response")
                return None
        else:
            print(f"❌ Failed to create content: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating content: {e}")
        return None

def test_direct_image_endpoints():
    """Test the direct image endpoints"""
    print("\n\n🧪 Testing Direct Image Endpoints")
    print("=" * 40)
    
    # Create a test workflow ID
    test_workflow_id = str(uuid.uuid4())
    
    # Test the regenerate-image endpoint
    print("\n1️⃣ Testing /regenerate-image endpoint...")
    
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
            print(f"🎯 Success: {result.get('success', 'Not specified')}")
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

def test_edit_image_endpoint():
    """Test the edit-image endpoint with form data"""
    print("\n\n🧪 Testing Edit Image Endpoint")
    print("=" * 40)
    
    # Create a test workflow ID
    test_workflow_id = str(uuid.uuid4())
    
    print("\n1️⃣ Testing /edit-image endpoint...")
    
    form_data = {
        "workflow_id": test_workflow_id,
        "prompt": "Add more plants around the workspace and make the lighting warmer and more inviting",
        "original_image_url": "https://placeholder.com/600x400/000000/FFFFFF/?text=Original+Workspace"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/edit-image",
            data=form_data,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Edit image endpoint working!")
            print(f"🎯 Success: {result.get('success', 'Not specified')}")
            print(f"📸 New image URL: {result.get('new_image_url', 'No URL')[:60]}...")
            print(f"💬 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Edit image endpoint failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing edit image: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Corrected API Tests")
    print("=" * 60)
    
    # Test 1: Create content (returns HTML)
    workflow_id = test_create_content()
    
    # Test 2: Direct image endpoints
    regenerate_success = test_direct_image_endpoints()
    
    # Test 3: Edit image endpoint
    edit_success = test_edit_image_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Create Content (HTML): {'✅ PASS' if workflow_id else '❌ FAIL'}")
    print(f"Regenerate Image: {'✅ PASS' if regenerate_success else '❌ FAIL'}")
    print(f"Edit Image: {'✅ PASS' if edit_success else '❌ FAIL'}")
    
    if regenerate_success and edit_success:
        print("\n🎉 Direct image endpoints are working correctly!")
        print("⚠️  Note: Create content returns HTML for browser rendering")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)