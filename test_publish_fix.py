#!/usr/bin/env python3
"""Test script to verify the publish functionality fix"""

import requests
import json

def test_publish_functionality():
    """Test the publish functionality with the fix"""
    
    # First, create content to get a workflow ID
    create_url = "http://localhost:8000/create-content"
    create_data = {
        "topic": "AI in healthcare",
        "tone": "professional", 
        "platforms": "linkedin,x",
        "include_image": True,
        "caption_length": "medium",
        "hashtag_count": 10
    }
    
    try:
        print("Step 1: Creating content to get workflow ID...")
        create_response = requests.post(create_url, data=create_data)
        
        if create_response.status_code == 200:
            # Extract workflow ID from the HTML response
            html_content = create_response.text
            import re
            workflow_match = re.search(r'workflow_id:\s*["\']([^"\']+)["\']', html_content)
            if workflow_match:
                workflow_id = workflow_match.group(1)
                print(f"✅ Got workflow ID: {workflow_id}")
                
                # Now test the publish functionality
                print("Step 2: Testing publish functionality...")
                publish_url = "http://localhost:8000/publish-content"
                
                # Prepare form data with selected_variants (platforms)
                publish_data = {
                    "workflow_id": workflow_id,
                    "selected_variants[linkedin]": "true",
                    "selected_variants[x]": "true"
                }
                
                publish_response = requests.post(publish_url, data=publish_data)
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    print(f"✅ SUCCESS: Publish request successful!")
                    print(f"Response: {result}")
                    return True
                else:
                    print(f"❌ FAILED: Publish request failed with status {publish_response.status_code}")
                    print(f"Response: {publish_response.text}")
                    return False
                    
            else:
                print("❌ FAILED: Could not extract workflow ID from HTML response")
                return False
        else:
            print(f"❌ FAILED: Content creation failed with status {create_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_publish_functionality()
    if success:
        print("\n🎉 All tests passed! The publish functionality fix is working.")
    else:
        print("\n❌ Tests failed. There may be additional issues.")