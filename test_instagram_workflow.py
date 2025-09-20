#!/usr/bin/env python3
"""
Instagram-specific workflow test script for AutoSocioly
Tests the complete Instagram workflow with ngrok integration
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.services.workflow_service import SocialMediaWorkflow
from src.services.auth_service import AuthService
from src.models import Platform, Tone
from src.utils.logger_config import setup_logging, get_logger

async def test_instagram_workflow():
    """Test the complete Instagram workflow with ngrok integration and posting"""
    
    print("📸 Instagram Workflow Test")
    print("=" * 50)
    
    # Initialize logging
    setup_logging()
    logger = get_logger('instagram_test')
    
    try:
        # Initialize workflow service
        print("🚀 Initializing Instagram workflow service...")
        workflow = SocialMediaWorkflow()
        
        # Verify auth service is properly initialized
        if not hasattr(workflow, 'auth_service'):
            print("❌ Auth service not initialized in workflow")
            return False
            
        print("✅ Auth service initialized")
        
        # Verify ngrok manager is available
        if not hasattr(workflow.auth_service, 'ngrok_manager'):
            print("❌ Ngrok manager not available")
            return False
            
        print("✅ Ngrok manager available")
        
        # Test 1: Generate content with Instagram-specific image
        print("\n🎨 Test 1: Generating Instagram content with image...")
        
        content_result = await workflow.create_content_workflow(
            topic="Create a stunning image of Ash and the pikachu",
            platforms=[Platform.INSTAGRAM],
            tone=Tone.ENGAGING,
            include_images=True,
            image_context="A beautiful golden hour sunset with silhouettes, perfect for Instagram engagement"
        )
        
        if not content_result.success:
            print(f"❌ Content generation failed: {content_result.error}")
            return False
            
        print("✅ Content generated successfully")
        print(f"📊 Generated {len(content_result.platform_content)} platform contents")
        print(f"🖼️  Generated {len(content_result.generated_images)} images")
        
        # Verify Instagram content exists
        if 'instagram' not in content_result.platform_content:
            print("❌ No Instagram content generated")
            return False
            
        instagram_content = content_result.platform_content['instagram']
        print(f"✅ Instagram content: {instagram_content[0]['content'][:100]}...")
        print(f"🏷️  Hashtags: {', '.join(instagram_content[0].get('hashtags', []))}")
        
        # Verify images were generated and stored as file paths
        if not content_result.generated_images:
            print("❌ No images generated")
            return False
            
        print("\n📁 Checking generated images...")
        public_urls = []
        for i, image_path in enumerate(content_result.generated_images):
            print(f"Image {i+1}: {image_path}")
            
            # Check if file exists
            if os.path.exists(image_path):
                print(f"✅ File exists: {image_path}")
                
                # Test ngrok conversion
                print(f"🌐 Testing ngrok conversion...")
                image_public_urls = workflow.auth_service.make_public_media_urls([image_path])
                
                if image_public_urls and image_public_urls[0]:
                    public_url = image_public_urls[0]
                    public_urls.append(public_url)
                    print(f"✅ Converted to: {public_url}")
                    
                    # Verify the public URL is accessible
                    try:
                        response = requests.get(public_url, timeout=10)
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '')
                            if content_type.startswith('image/'):
                                print(f"✅ Public URL is accessible and returns an image ({content_type})")
                            else:
                                print(f"⚠️  Public URL returns: {content_type}")
                        else:
                            print(f"❌ Public URL returned status: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Failed to access public URL: {e}")
                else:
                    print(f"❌ Failed to convert to public URL")
            else:
                print(f"❌ File not found: {image_path}")
                return False
        
        # Test 2: Post the content to Instagram
        print("\n📤 Test 2: Posting content to Instagram...")
        
        # Prepare content data for posting
        content_data = {
            "platform_content": content_result.platform_content,
            "generated_images": content_result.generated_images,
            "public_images": [{"public_url": url, "local_path": path} for url, path in zip(public_urls, content_result.generated_images)],
            "publishNow": True  # Post immediately for testing
        }
        
        # Post to Instagram using the workflow's posting method
        posting_result = await workflow.post_content_workflow(
            content_data=content_data,
            platforms=[Platform.INSTAGRAM],
            publish_now=True
        )
        
        if not posting_result.success:
            print(f"❌ Instagram posting failed: {posting_result.error}")
            return False
            
        print("✅ Instagram posting successful!")
        print(f"📊 Posting results: {json.dumps(posting_result.results, indent=2)}")
        
        # Verify Instagram posting specifically
        if 'instagram' in posting_result.results:
            instagram_result = posting_result.results['instagram']
            if instagram_result.get('success'):
                print(f"✅ Instagram post created successfully!")
                print(f"📝 Post ID: {instagram_result.get('post_id', 'N/A')}")
                print(f"🔗 Post URL: {instagram_result.get('post_url', 'N/A')}")
            else:
                print(f"❌ Instagram posting failed: {instagram_result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No Instagram posting results found")
            return False
            
    except Exception as e:
        print(f"❌ Instagram workflow test failed: {e}")
        logger.error(f"Instagram workflow test failed", extra={
            'error': str(e),
            'error_type': type(e).__name__
        })
        return False

async def test_instagram_scheduled_posting():
    """Test Instagram scheduled posting functionality"""
    
    print("\n📅 Test 3: Instagram Scheduled Posting")
    print("-" * 40)
    
    # Initialize logging
    setup_logging()
    logger = get_logger('instagram_scheduled_test')
    
    try:
        # Initialize workflow service
        workflow = SocialMediaWorkflow()
        
        # Generate content first
        print("🎨 Generating Instagram content for scheduled posting...")
        
        content_result = await workflow.create_content_workflow(
            topic="Morning coffee motivation for tomorrow",
            platforms=[Platform.INSTAGRAM],
            tone=Tone.ENGAGING,
            include_images=True,
            image_context="A beautiful morning coffee scene with motivational vibes"
        )
        
        if not content_result.success:
            print(f"❌ Content generation failed: {content_result.error}")
            return False
            
        print("✅ Content generated successfully")
        
        # Convert images to public URLs
        public_urls = []
        for image_path in content_result.generated_images:
            if os.path.exists(image_path):
                image_public_urls = workflow.auth_service.make_public_media_urls([image_path])
                if image_public_urls and image_public_urls[0]:
                    public_urls.append(image_public_urls[0])
        
        if not public_urls:
            print("❌ Failed to convert images to public URLs")
            return False
            
        print(f"✅ Converted {len(public_urls)} images to public URLs")
        
        # Schedule for 5 minutes from now
        from datetime import datetime, timedelta
        schedule_time = datetime.now() + timedelta(minutes=5)
        schedule_time_str = schedule_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"📅 Scheduling post for: {schedule_time_str}")
        
        # Prepare content data for scheduled posting
        content_data = {
            "platform_content": content_result.platform_content,
            "generated_images": content_result.generated_images,
            "public_images": [{"public_url": url, "local_path": path} for url, path in zip(public_urls, content_result.generated_images)],
            "scheduledFor": schedule_time_str
        }
        
        # Post to Instagram with scheduling
        posting_result = await workflow.post_content_workflow(
            content_data=content_data,
            platforms=[Platform.INSTAGRAM],
            scheduled_for=schedule_time_str
        )
        
        if not posting_result.success:
            print(f"❌ Instagram scheduled posting failed: {posting_result.error}")
            return False
            
        print("✅ Instagram scheduled posting successful!")
        
        # Verify Instagram posting specifically
        if 'instagram' in posting_result.results:
            instagram_result = posting_result.results['instagram']
            if instagram_result.get('success'):
                print(f"✅ Instagram post scheduled successfully!")
                print(f"📝 Post ID: {instagram_result.get('post_id', 'N/A')}")
                print(f"⏰ Scheduled for: {schedule_time_str}")
                print(f"🔗 Post URL: {instagram_result.get('post_url', 'N/A')}")
                return True
            else:
                print(f"❌ Instagram scheduled posting failed: {instagram_result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No Instagram posting results found")
            return False
            
    except Exception as e:
        print(f"❌ Instagram scheduled posting test failed: {e}")
        logger.error(f"Instagram scheduled posting test failed", extra={
            'error': str(e),
            'error_type': type(e).__name__
        })
        return False

async def test_instagram_image_requirements():
    """Test Instagram-specific image requirements"""
    
    print("\n📐 Test 4: Instagram Image Requirements")
    print("-" * 40)
    
    workflow = SocialMediaWorkflow()
    
    try:
        # Test with image generation
        result = await workflow.create_content_workflow(
            topic="Coffee art and morning motivation",
            platforms=[Platform.INSTAGRAM],
            tone=Tone.ENGAGING,
            include_images=True,
            image_context="Beautiful latte art with motivational text overlay"
        )
        
        if result.success and result.generated_images:
            print("✅ Instagram content with image generated")
            
            # Check image specifications
            for image_path in result.generated_images:
                if os.path.exists(image_path):
                    from PIL import Image
                    with Image.open(image_path) as img:
                        width, height = img.size
                        print(f"📏 Image dimensions: {width}x{height}")
                        
                        # Check if it's square (Instagram prefers square)
                        if width == height:
                            print("✅ Image is square (Instagram optimal)")
                        else:
                            aspect_ratio = width / height
                            print(f"📐 Aspect ratio: {aspect_ratio:.2f}")
                            if 0.8 <= aspect_ratio <= 1.2:
                                print("✅ Aspect ratio is Instagram-friendly")
                            else:
                                print("⚠️  Aspect ratio may need adjustment for Instagram")
            
            return True
        else:
            print("❌ Failed to generate Instagram content with images")
            return False
            
    except Exception as e:
        print(f"❌ Instagram requirements test failed: {e}")
        return False

async def main():
    """Run Instagram workflow tests"""
    
    print("🎯 Instagram Workflow Test Suite")
    print("=" * 60)
    print("Testing complete Instagram workflow with ngrok integration")
    print()
    
    # Run all tests
    tests = [
        test_instagram_workflow,
        test_instagram_scheduled_posting,
        test_instagram_image_requirements
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"🎯 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Instagram workflow tests passed!")
        print("✅ Instagram posting functionality working")
        print("✅ Instagram scheduled posting working")
        print("✅ Complete workflow from content creation to posting")
        print("✅ Complete workflow from content creation to scheduled posting")
        return True
    else:
        print("❌ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)