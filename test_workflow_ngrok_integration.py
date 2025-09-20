#!/usr/bin/env python3
"""
Test Workflow Ngrok Integration
Verifies that the workflow service properly converts local image paths to ngrok URLs
"""

import asyncio
import json
import os
from pathlib import Path
from src.services.workflow_service import SocialMediaWorkflow
from src.models import Platform, Tone

async def test_workflow_ngrok_integration():
    """Test that workflow service converts local image paths to ngrok URLs"""
    
    print("=== Testing Workflow Ngrok Integration ===")
    
    # Initialize workflow
    workflow = SocialMediaWorkflow()
    
    # Check if auth service is properly initialized
    if not hasattr(workflow, 'auth_service'):
        print("❌ Auth service not initialized in workflow")
        return False
    
    print("✓ Auth service initialized in workflow")
    
    # Check if ngrok manager is available
    if not hasattr(workflow.auth_service, 'ngrok_manager'):
        print("❌ Ngrok manager not available in auth service")
        return False
    
    print("✓ Ngrok manager available in auth service")
    
    # Test image path to URL conversion
    test_image_path = "static/uploads/generated_20250920_165051_2251.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    print(f"✓ Test image found: {test_image_path}")
    
    # Test the make_public_media_urls method
    try:
        public_urls = workflow.auth_service.make_public_media_urls([test_image_path])
        
        if not public_urls:
            print("❌ Failed to convert image path to public URL")
            return False
        
        public_url = public_urls[0]
        print(f"✓ Converted local path to public URL: {public_url}")
        
        # Verify the URL is accessible
        import requests
        response = requests.get(public_url, timeout=10)
        
        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image/"):
            print("✓ Public URL is accessible and returns an image")
            return True
        else:
            print(f"❌ Public URL test failed: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing URL conversion: {e}")
        return False

async def test_content_workflow_with_images():
    """Test the complete content workflow with image generation"""
    
    print("\n=== Testing Content Workflow with Images ===")
    
    workflow = SocialMediaWorkflow()
    
    try:
        # Test content generation with images
        content_response = await workflow.create_content_workflow(
            topic="Hydration and productivity",
            platforms=[Platform.INSTAGRAM],
            tone=Tone.PROFESSIONAL,
            include_images=True,
            image_context="A refreshing glass of water on a desk with a laptop in the background"
        )
        
        if not content_response.success:
            print(f"❌ Content generation failed: {content_response.error}")
            return False
        
        print("✓ Content generation successful")
        print(f"✓ Generated {len(content_response.generated_images)} images")
        
        # Verify images were generated
        if not content_response.generated_images:
            print("❌ No images were generated")
            return False
        
        # Check if generated images exist locally
        for image_path in content_response.generated_images:
            # Convert web URL back to local file path for existence check
            if image_path.startswith('http'):
                # Extract filename from URL
                filename = os.path.basename(image_path)
                local_path = os.path.join('static/uploads', filename)
            else:
                local_path = image_path
                
            if os.path.exists(local_path):
                print(f"✓ Generated image exists: {local_path}")
            else:
                print(f"❌ Generated image not found: {local_path}")
                return False
        
        # Test that the workflow can convert these to public URLs
        public_urls = workflow.auth_service.make_public_media_urls(content_response.generated_images)
        
        if not public_urls or len(public_urls) != len(content_response.generated_images):
            print("❌ Failed to convert all generated images to public URLs")
            return False
        
        print(f"✓ Successfully converted {len(public_urls)} images to public URLs")
        
        for url in public_urls:
            print(f"  - {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing content workflow: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("Testing Workflow Ngrok Integration")
    print("=" * 50)
    
    # Test 1: Basic ngrok integration
    test1_success = await test_workflow_ngrok_integration()
    
    # Test 2: Complete workflow with images
    test2_success = await test_content_workflow_with_images()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Basic Ngrok Integration: {'✓ PASS' if test1_success else '❌ FAIL'}")
    print(f"Content Workflow with Images: {'✓ PASS' if test2_success else '❌ FAIL'}")
    
    overall_success = test1_success and test2_success
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)