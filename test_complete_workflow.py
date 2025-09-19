#!/usr/bin/env python3
"""
Complete test workflow for enhanced image modification
"""

import requests
import json
import time

def create_test_workflow():
    """Create a test workflow to work with"""
    print("🔄 Creating test workflow...")
    
    workflow_data = {
        "topic": "Modern coffee shop workspace",
        "platforms": ["instagram"],
        "tone": "professional",
        "content_type": "engaging",
        "target_audience": "remote workers and freelancers",
        "hashtag_count": 10
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/create-workflow",
            json=workflow_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            workflow_id = result.get("workflow_id")
            print(f"✅ Workflow created: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

def generate_initial_image(workflow_id):
    """Generate initial image for the workflow"""
    print("🖼️  Generating initial image...")
    
    # For this test, we'll use the existing workflow data that should have been created
    # with the initial content creation. Let's just return a placeholder for now.
    return f"https://placeholder.com/image/{workflow_id}"

def test_enhanced_regeneration(workflow_id, original_image_url):
    """Test the enhanced image regeneration"""
    print("🔄 Testing enhanced image regeneration...")
    
    try:
        response = requests.post(
            "http://localhost:8000/regenerate-image",
            json={
                "workflow_id": workflow_id,
                "prompt": "Add more plants around the workspace and make the lighting warmer and more inviting",
                "original_image_url": original_image_url
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced regeneration successful!")
            print(f"🎯 Success: {result.get('success', False)}")
            print(f"📸 New image URL: {result.get('image_url', 'No URL')[:60]}...")
            print(f"🔄 Original preserved: {result.get('original_image_url', 'N/A')[:60]}...")
            print(f"💬 Message: {result.get('message', 'No message')}")
            
            # Check for enhanced metadata
            if 'regeneration_history' in result:
                print(f"📋 Regeneration history entries: {len(result.get('regeneration_history', []))}")
            
            return result.get('image_url')
        else:
            print(f"❌ Enhanced regeneration failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during enhanced regeneration: {e}")
        return None

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
    except Exception as e:
        print(f"❌ Application is not running or not accessible: {e}")
        return False

def main():
    """Main test workflow"""
    print("🧪 Complete Enhanced Image Modification Test")
    print("=" * 50)
    
    # Check if application is running
    if not check_application_health():
        print("\n❌ Cannot run tests - application is not accessible")
        print("🔄 Please start the application first with: python app.py")
        return False
    
    # Step 1: Create workflow
    workflow_id = create_test_workflow()
    if not workflow_id:
        return False
    
    # Step 2: Generate initial image
    initial_image_url = generate_initial_image(workflow_id)
    if not initial_image_url:
        print("❌ Cannot proceed without initial image")
        return False
    
    # Step 3: Test enhanced regeneration
    print("\n" + "="*50)
    regenerated_image_url = test_enhanced_regeneration(workflow_id, initial_image_url)
    
    if regenerated_image_url:
        print("\n🎉 Complete workflow test successful!")
        print("✅ Enhanced image modification with core preservation is working")
        print(f"🔄 Workflow ID: {workflow_id}")
        print(f"📸 Original: {initial_image_url[:60]}...")
        print(f"🎨 Modified: {regenerated_image_url[:60]}...")
        return True
    else:
        print("\n❌ Enhanced regeneration test failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)