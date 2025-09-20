#!/usr/bin/env python3
"""
Debug script to test image generation and URL creation
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.image_gen import ImageGenerationService
from src.utils.ngrok_manager import NgrokManager
from src.services.user_workflow_service import UserWorkflowService
from src.services.text_gen import TextGenerationService
from src.services.poster_service import PosterService
from src.utils.logger_config import get_logger

logger = get_logger('debug_image_issue')

async def test_image_generation_and_url_creation():
    """Test the complete image generation and URL creation flow"""
    
    print("=== Testing Image Generation and URL Creation ===")
    
    try:
        # Initialize services
        print("1. Initializing services...")
        from src.services.getlate_service import GetLateService
        image_gen = ImageGenerationService()
        ngrok_manager = NgrokManager()
        text_gen = TextGenerationService()
        getlate_service = GetLateService()
        poster_service = PosterService(getlate_service)
        
        # Test image generation
        print("2. Testing image generation...")
        test_topic = "Beautiful sunset over mountains"
        test_platform = "instagram"
        
        image_data = await image_gen.generate_social_media_image(
            topic=test_topic,
            platform=test_platform,
            style="engaging"
        )
        
        print(f"Image generated: {image_data.get('image_url')}")
        print(f"Filepath: {image_data.get('filepath')}")
        print(f"Success: {image_data.get('metadata', {}).get('success')}")
        
        # Check if file exists
        filepath = image_data.get('filepath')
        if filepath:
            file_exists = Path(filepath).exists()
            print(f"File exists: {file_exists}")
            
            if file_exists:
                file_size = Path(filepath).stat().st_size
                print(f"File size: {file_size} bytes")
        
        # Test ngrok URL creation
        print("\n3. Testing ngrok URL creation...")
        
        # Check ngrok status first
        ngrok_status = ngrok_manager.get_ngrok_status()
        print(f"Ngrok status: {ngrok_status}")
        
        if ngrok_status.get('ngrok_running'):
            public_url = ngrok_manager.create_public_url(filepath)
            print(f"Public URL created: {public_url}")
            
            # Test if URL is accessible
            import requests
            try:
                response = requests.get(public_url, timeout=10)
                print(f"URL accessible: {response.status_code == 200}")
                print(f"Content-Type: {response.headers.get('content-type')}")
            except Exception as e:
                print(f"URL test failed: {e}")
        else:
            print("Ngrok not running, cannot create public URL")
        
        # Test the complete workflow service flow
        print("\n4. Testing complete workflow service flow...")
        
        workflow_service = UserWorkflowService(
            text_generation_service=text_gen,
            image_generation_service=image_gen,
            ngrok_manager=ngrok_manager,
            poster_service=poster_service
        )
        
        # Test process_user_input
        result = await workflow_service.process_user_input(
            user_input="Beautiful sunset photography tips",
            platforms=["instagram"],
            tone="engaging",
            include_image=True
        )
        
        print(f"Workflow result success: {result.get('success')}")
        print(f"Session ID: {result.get('session_id')}")
        
        if result.get('success'):
            session_id = result.get('session_id')
            content_package = result.get('content', {})
            
            print(f"Images count: {len(content_package.get('images', []))}")
            print(f"Public images count: {len(content_package.get('public_images', []))}")
            
            # Check each public image
            for i, img in enumerate(content_package.get('public_images', [])):
                print(f"Public image {i+1}:")
                print(f"  Public URL: {img.get('public_url')}")
                print(f"  Accessible: {img.get('accessible')}")
                print(f"  Original filepath: {img.get('filepath')}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation_and_url_creation())