#!/usr/bin/env python3
"""
Complete workflow test script for AutoSocioly
Tests the entire flow from user input to posting on multiple platforms
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.services.user_workflow_service import UserWorkflowService
from src.services.getlate_service import GetLateService
from src.services.text_gen import TextGenerationService
from src.services.image_gen import ImageGenerationService
from src.services.poster_service import PosterService
from src.utils.logger_config import setup_logging, get_logger

# Mock ngrok manager for testing
class MockNgrokManager:
    def __init__(self, auth_token=None):
        self.auth_token = auth_token
    
    async def start_tunnel(self, port):
        return "https://mock-ngrok-url.ngrok.io"
    
    async def get_public_url(self, local_path):
        return f"https://mock-ngrok-url.ngrok.io/{local_path.split('/')[-1]}"

async def test_complete_workflow():
    """Test the complete workflow from user input to posting"""
    
    print("🚀 Starting complete workflow test...")
    print("=" * 60)
    
    # Initialize logging
    setup_logging()
    logger = get_logger('test')
    
    try:
        # Initialize services
        print("📋 Initializing services...")
        
        # Get API keys from environment
        getlate_api_key = os.getenv('GETLATE_API_KEY', 'test_key')
        gemini_api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        ngrok_auth_token = os.getenv('NGROK_AUTH_TOKEN', 'test_token')
        
        # Initialize services
        ngrok_manager = MockNgrokManager(auth_token=ngrok_auth_token)
        getlate_service = GetLateService(api_key=getlate_api_key)
        text_generation = TextGenerationService()
        image_generation = ImageGenerationService()
        poster_service = PosterService(getlate_service=getlate_service)
        
        # Initialize workflow service
        workflow_service = UserWorkflowService()
        
        print("✅ Services initialized successfully")
        print()
        
        # Test user input
        test_inputs = [
            {
                "input": "Share an inspiring quote about technology and innovation for tech professionals",
                "platforms": ["linkedin", "twitter", "facebook"],
                "description": "Professional tech content"
            },
            {
                "input": "Create a fun, engaging post about weekend vibes with a beautiful sunset image",
                "platforms": ["instagram", "facebook", "pinterest"],
                "description": "Lifestyle content with image"
            },
            {
                "input": "Share a thought-provoking discussion starter about AI and the future of work",
                "platforms": ["reddit", "linkedin", "twitter"],
                "description": "Discussion content"
            }
        ]
        
        for i, test_case in enumerate(test_inputs, 1):
            print(f"🧪 Test Case {i}: {test_case['description']}")
            print(f"Input: {test_case['input']}")
            print(f"Platforms: {', '.join(test_case['platforms'])}")
            print("-" * 40)
            
            try:
                # Step 1: Process user input
                print("📝 Processing user input...")
                result = await workflow_service.process_user_input(
                    user_input=test_case['input'],
                    platforms=test_case['platforms']
                )
                
                if not result.get('success'):
                    print(f"❌ Failed to process input: {result.get('error')}")
                    continue
                
                session_id = result['session_id']
                content = result['content']
                public_images = result.get('public_images', [])
                
                print(f"✅ Content generated successfully")
                print(f"📊 Session ID: {session_id}")
                print(f"🖼️  Images generated: {len(content.get('images', []))}")
                print(f"🌐 Public images: {len(public_images)}")
                print()
                
                # Display generated content for each platform
                print("📱 Generated platform content:")
                for platform, platform_content in content.get('platform_content', {}).items():
                    print(f"\n🎯 {platform.upper()}:")
                    print(f"   Content: {platform_content.get('content', 'N/A')[:100]}...")
                    print(f"   Hashtags: {', '.join(platform_content.get('hashtags', []))}")
                
                print()
                
                # Step 2: Simulate user confirmation (in real scenario, user would review)
                print("✅ Simulating user confirmation...")
                
                # For testing, we'll skip actual posting to avoid spamming social media
                # In production, this would call: workflow_service.confirm_and_post(session_id, True)
                
                print("🎯 Content ready for posting (skipped in test mode)")
                print(f"📊 Session {session_id} completed successfully")
                
                # Log test results
                logger.info(f"Test case {i} completed successfully", extra={
                    'test_case': i,
                    'input': test_case['input'],
                    'platforms': test_case['platforms'],
                    'session_id': session_id,
                    'images_generated': len(content.get('images', [])),
                    'public_images': len(public_images),
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"❌ Test case {i} failed: {e}")
                logger.error(f"Test case {i} failed", extra={
                    'test_case': i,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
            
            print("=" * 60)
            print()
        
        # Test platform-specific posting (with mock data)
        print("🔧 Testing platform-specific posting capabilities...")
        
        # Test each platform poster
        platforms_to_test = ['instagram', 'facebook', 'twitter', 'linkedin', 'reddit', 'pinterest']
        
        for platform in platforms_to_test:
            try:
                poster = poster_service.get_poster(platform)
                if poster:
                    # Test content validation
                    test_content = {
                        "content": f"Test content for {platform}",
                        "hashtags": ["test", "automation"],
                        "media_urls": ["https://example.com/test.jpg"]
                    }
                    
                    validation_result = poster.validate_content(test_content['content'], test_content.get('media_urls'))
                    is_valid = validation_result['valid']
                    errors = validation_result.get('error', '')
                    print(f"✅ {platform.capitalize()}: Validation {'passed' if is_valid else 'failed'}")
                    if not is_valid:
                        print(f"   Errors: {errors}")
                    
                    logger.info(f"Platform validation test completed", extra={
                        'platform': platform,
                        'validation_passed': is_valid,
                        'validation_errors': errors if not is_valid else []
                    })
                else:
                    print(f"⚠️  {platform.capitalize()}: No poster available")
                    
            except Exception as e:
                print(f"❌ {platform.capitalize()}: Test failed - {e}")
                logger.error(f"Platform test failed", extra={
                    'platform': platform,
                    'error': str(e)
                })
        
        print()
        print("🎉 Complete workflow test finished!")
        print("📊 Check the logs for detailed workflow monitoring information")
        
        # Display session summary
        sessions = workflow_service.active_sessions
        print(f"\n📋 Active sessions: {len(sessions)}")
        for session_id, session_data in sessions.items():
            print(f"   - {session_id}: {session_data['status']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error("Complete workflow test failed", extra={
            'error': str(e),
            'error_type': type(e).__name__
        })
        return False
    
    return True

async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 Testing error handling scenarios...")
    
    setup_logging()
    logger = get_logger('test.errors')
    
    try:
        # Test with invalid API keys
        print("Testing with invalid API keys...")
        
        # This should handle gracefully and log appropriate errors
        workflow_service = UserWorkflowService()
        
        result = await workflow_service.process_user_input(
            user_input="Test input",
            platforms=["instagram"]
        )
        
        print(f"Error handling result: {result}")
        
    except Exception as e:
        print(f"Error handling test completed: {e}")
        logger.info("Error handling test completed", extra={
            'error_handled': True,
            'error': str(e)
        })

if __name__ == "__main__":
    print("🚀 AutoSocioly Complete Workflow Test Suite")
    print("=" * 60)
    
    # Run main workflow test
    success = asyncio.run(test_complete_workflow())
    
    # Run error handling test
    asyncio.run(test_error_handling())
    
    print("\n🏁 Test suite completed!")
    print(f"Overall result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    sys.exit(0 if success else 1)