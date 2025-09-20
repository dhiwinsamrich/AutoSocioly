#!/usr/bin/env python3
"""
Complete workflow test - simulates the entire process from image generation to posting
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.image_gen import ImageGenerationService
from src.services.user_workflow_service import UserWorkflowService
from src.services.getlate_service import GetLateService
from src.services.poster_service import PosterService
from src.utils.ngrok_manager import NgrokManager

async def test_complete_workflow():
    """Test the complete workflow from image generation to posting"""
    
    print("=== Complete Workflow Test ===")
    
    try:
        # Initialize services
        print("1. Initializing services...")
        workflow_service = UserWorkflowService()
        # Get the services from the workflow service
        image_service = workflow_service.image_gen
        ngrok_manager = workflow_service.ngrok_manager
        print("✅ Services initialized")
        
        # Test image generation
        print("\n2. Testing image generation...")
        image_result = await image_service.generate_social_media_image(
            topic="A beautiful sunset over mountains with inspirational text overlay",
            platform="instagram",
            style="artistic",
            include_text=True,
            text_content="Inspiration comes from within",
            color_scheme=["warm", "orange", "yellow"]
        )
        
        if not image_result.get('metadata', {}).get('success'):
            print("❌ Image generation failed")
            return False
            
        filepath = image_result.get('filepath')
        image_url = image_result.get('image_url')
        
        print(f"✅ Image generated:")
        print(f"   - Filepath: {filepath}")
        print(f"   - Image URL: {image_url}")
        
        # Test making image public
        print("\n3. Testing public URL creation...")
        
        # Check if file exists
        if filepath and Path(filepath).exists():
            print(f"✅ File exists: {Path(filepath).stat().st_size} bytes")
            
            # Create public URL
            public_url = ngrok_manager.create_public_url(filepath)
            if public_url:
                print(f"✅ Public URL created: {public_url}")
            else:
                print("❌ Failed to create public URL")
                return False
        else:
            print(f"❌ File not found: {filepath}")
            return False
        
        # Test workflow service image processing
        print("\n4. Testing workflow service image processing...")
        
        # Create mock image data similar to what would be in session
        image_data = {
            'filepath': filepath,
            'image_url': image_url,
            'platform': 'instagram',
            'topic': 'A beautiful sunset over mountains with inspirational text overlay',
            'metadata': image_result.get('metadata', {})
        }
        
        # Test the _make_images_public method
        processed_images = await workflow_service._make_images_public([image_data])
        
        if processed_images and len(processed_images) > 0:
            processed_image = processed_images[0]
            print(f"✅ Image processed by workflow service:")
            print(f"   - Original filepath: {processed_image.get('filepath')}")
            print(f"   - Public URL: {processed_image.get('public_url')}")
            print(f"   - Accessible: {processed_image.get('accessible')}")
            
            if processed_image.get('accessible'):
                print("✅ Image is accessible for posting!")
                
                # Test actual posting (mock)
                print("\n5. Testing content posting (mock)...")
                
                # Create mock content data
                content_data = {
                    'platform': 'instagram',
                    'content': 'A beautiful sunset over mountains with inspirational text overlay',
                    'images': processed_images,
                    'metadata': {
                        'topic': 'A beautiful sunset over mountains with inspirational text overlay',
                        'style': 'artistic'
                    }
                }
                
                # This would normally call poster_service.post_to_platform
                # For testing, we'll just verify the data structure
                print("✅ Content data prepared for posting:")
                print(f"   - Platform: {content_data['platform']}")
                print(f"   - Content: {content_data['content']}")
                print(f"   - Images: {len(content_data['images'])} image(s)")
                print(f"   - First image public URL: {content_data['images'][0].get('public_url')}")
                
                return True
            else:
                print("❌ Image is not accessible")
                return False
        else:
            print("❌ Failed to process images")
            return False
            
    except Exception as e:
        print(f"❌ Error in workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_complete_workflow())
    print(f"\n=== Final Result ===")
    print(f"Complete workflow test: {'SUCCESS' if result else 'FAILED'}")