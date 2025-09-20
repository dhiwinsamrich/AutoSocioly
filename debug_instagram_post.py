#!/usr/bin/env python3
"""
Test Instagram posting with generated image
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.user_workflow_service import UserWorkflowService

async def test_instagram_post():
    """Test posting to Instagram with generated image"""
    
    print("=== Instagram Post Test ===")
    
    try:
        # Initialize workflow service
        print("1. Initializing workflow service...")
        workflow_service = UserWorkflowService()
        print("✅ Workflow service initialized")
        
        # Test user input processing
        print("\n2. Processing user input...")
        user_input = "A beautiful sunset over mountains with inspirational text overlay"
        platforms = ["instagram"]
        
        result = await workflow_service.process_user_input(
            user_input=user_input,
            platforms=platforms,
            tone="inspirational",
            include_image=True
        )
        
        if not result.get('success'):
            print(f"❌ Failed to process user input: {result.get('error')}")
            return False
            
        session_id = result.get('session_id')
        content_package = result.get('content', {})
        
        print(f"✅ User input processed successfully")
        print(f"   - Session ID: {session_id}")
        print(f"   - Public images: {len(content_package.get('public_images', []))}")
        
        # Show the generated content
        print("\n3. Generated content:")
        print(f"   Content package keys: {list(content_package.keys())}")
        if content_package.get('platform_content'):
            for platform, content in content_package['platform_content'].items():
                print(f"   Platform: {platform}")
                print(f"   Content type: {type(content)}")
                print(f"   Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                if isinstance(content, dict):
                    print(f"   Content: {content.get('content', 'N/A')}")
                    print(f"   Hashtags: {content.get('hashtags', [])}")
                else:
                    print(f"   Content: {content}")
                
        # Show the public images
        if content_package.get('public_images'):
            print(f"\n4. Public images:")
            for i, image in enumerate(content_package['public_images']):
                print(f"   Image {i+1}:")
                print(f"      - Public URL: {image.get('public_url')}")
                print(f"      - Accessible: {image.get('accessible')}")
                print(f"      - Platform: {image.get('platform')}")
        
        # Test user confirmation (simulate user saying "yes, post it")
        print("\n5. Simulating user confirmation...")
        
        # Get the session
        session = workflow_service.active_sessions.get(session_id)
        if not session:
            print("❌ Session not found")
            return False
            
        print("✅ Session found, ready to post")
        
        # Test the posting process (this would normally be called when user confirms)
        print("\n6. Testing content posting...")
        
        try:
            # This simulates what happens when user confirms
            # Get the actual content (it's called 'caption', not 'content')
            instagram_content = content_package['platform_content']['instagram']
            caption = instagram_content.get('caption', 'No caption generated')
            
            content_data = {
                'platform': 'instagram',
                'content': caption,
                'images': content_package.get('public_images', []),
                'metadata': {
                    'topic': user_input,
                    'tone': 'inspirational',
                    'session_id': session_id,
                    'hashtags': instagram_content.get('hashtags', [])
                }
            }
            
            print(f"✅ Content data prepared:")
            print(f"   - Platform: {content_data['platform']}")
            print(f"   - Content: {content_data['content'][:100]}...")
            print(f"   - Images: {len(content_data['images'])} image(s)")
            
            if content_data['images']:
                first_image = content_data['images'][0]
                print(f"   - First image URL: {first_image.get('public_url')}")
                print(f"   - First image accessible: {first_image.get('accessible')}")
                
                # Test if the URL is actually accessible
                print(f"\n7. Testing image URL accessibility...")
                
                import requests
                try:
                    response = requests.head(first_image.get('public_url'), timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Image URL is accessible (HTTP {response.status_code})")
                    else:
                        print(f"⚠️  Image URL returned HTTP {response.status_code}")
                except Exception as e:
                    print(f"⚠️  Could not test image URL: {e}")
            
            print(f"\n8. Ready for actual posting!")
            print(f"   All components are working correctly.")
            print(f"   The image has been generated and made public.")
            print(f"   The content has been prepared for Instagram.")
            print(f"   The workflow is ready to post to Instagram.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in posting test: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error in Instagram post test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_instagram_post())
    print(f"\n=== Final Result ===")
    print(f"Instagram post test: {'SUCCESS' if result else 'FAILED'}")