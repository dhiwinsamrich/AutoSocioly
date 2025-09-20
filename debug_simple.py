#!/usr/bin/env python3
"""
Simple debug script to test image generation and URL creation without API dependencies
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.image_gen import ImageGenerationService
from src.utils.logger_config import get_logger

logger = get_logger('debug_simple')

async def test_image_generation():
    """Test image generation and file saving"""
    try:
        print("=== Testing Image Generation ===")
        
        # Initialize image generation service
        print("1. Initializing image generation service...")
        image_gen_service = ImageGenerationService()
        
        # Test image generation
        print("2. Generating test image...")
        test_prompt = "A beautiful sunset over mountains with inspirational text overlay"
        platform = "instagram"
        
        result = await image_gen_service.generate_social_media_image(
            topic=test_prompt,
            platform=platform,
            color_scheme=["warm", "orange", "yellow"],
            include_text=True,
            text_content="Inspiration comes from within"
        )
        
        print(f"Image generation result:")
        print(f"  Success: {result.get('metadata', {}).get('success', False)}")
        print(f"  Image URL: {result.get('image_url', 'N/A')}")
        print(f"  Filepath: {result.get('filepath', 'N/A')}")
        print(f"  Error: {result.get('error', 'None')}")
        
        # Check if file actually exists
        if result.get('filepath'):
            local_path = result['filepath']
            print(f"3. Checking if file exists: {local_path}")
            
            # Convert to absolute path if relative
            if not os.path.isabs(local_path):
                local_path = os.path.join(os.path.dirname(__file__), local_path.lstrip('/'))
            
            exists = os.path.exists(local_path)
            print(f"  File exists: {exists}")
            
            if exists:
                file_size = os.path.getsize(local_path)
                print(f"  File size: {file_size} bytes")
                
                # Try to create a simple public URL
                print(f"4. Testing URL creation...")
                
                # Create a simple HTTP URL (this would normally use ngrok)
                # For testing, we'll just create a file:// URL
                public_url = f"file:///{local_path.replace('\\', '/')}"
                print(f"  Public URL: {public_url}")
                
                return {
                'success': True,
                'local_path': local_path,
                'public_url': public_url,
                'image_url': result.get('image_url'),
                'image_data': result
            }
            else:
                print(f"  ERROR: Generated file not found!")
                return {
                    'success': False,
                    'error': 'Generated file not found on disk'
                }
        else:
            print(f"  ERROR: No local path in result!")
            return {
                'success': False,
                'error': 'No local path returned from image generation'
            }
            
    except Exception as e:
        error_msg = f"Error during image generation test: {str(e)}"
        print(f"ERROR: {error_msg}")
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }

if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("static/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created uploads directory: {uploads_dir.absolute()}")
    
    # Run the test
    result = asyncio.run(test_image_generation())
    
    print(f"\n=== Final Result ===")
    print(f"Success: {result['success']}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    if 'local_path' in result:
        print(f"Local path: {result['local_path']}")
    if 'public_url' in result:
        print(f"Public URL: {result['public_url']}")