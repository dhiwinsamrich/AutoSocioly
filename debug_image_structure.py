#!/usr/bin/env python3
"""
Debug script to examine the complete image data structure
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.image_gen import ImageGenerationService
from src.utils.logger_config import get_logger

logger = get_logger('debug_image_structure')

async def examine_image_structure():
    """Examine the complete image data structure"""
    try:
        print("=== Examining Image Data Structure ===")
        
        # Initialize image generation service
        print("1. Initializing image generation service...")
        image_gen_service = ImageGenerationService()
        
        # Test image generation
        print("2. Generating test image...")
        test_topic = "A beautiful sunset over mountains with inspirational text overlay"
        platform = "instagram"
        
        result = await image_gen_service.generate_social_media_image(
            topic=test_topic,
            platform=platform,
            color_scheme=["warm", "orange", "yellow"],
            include_text=True,
            text_content="Inspiration comes from within"
        )
        
        print(f"\n=== Complete Image Data Structure ===")
        print(json.dumps(result, indent=2, default=str))
        
        print(f"\n=== Key Fields Analysis ===")
        print(f"image_url: {result.get('image_url', 'MISSING')}")
        print(f"filepath: {result.get('filepath', 'MISSING')}")
        print(f"local_path: {result.get('local_path', 'MISSING')}")
        print(f"image_path: {result.get('image_path', 'MISSING')}")
        
        # Check what the workflow service expects
        print(f"\n=== Workflow Service Compatibility Check ===")
        
        # Simulate what _make_images_public does
        image_path = result.get("image_path") or result.get("local_path") or result.get("filepath")
        print(f"Selected image_path: {image_path}")
        
        if image_path:
            path_exists = Path(image_path).exists()
            print(f"Path exists: {path_exists}")
            
            if path_exists:
                print("✅ Image would be processed by _make_images_public")
                
                # Create a mock public URL
                public_url = f"http://localhost:8080{result.get('image_url', '')}"
                print(f"Mock public URL would be: {public_url}")
                
                return {
                    'success': True,
                    'image_path': image_path,
                    'public_url': public_url,
                    'original_data': result
                }
            else:
                print("❌ Image file not found on disk")
                return {
                    'success': False,
                    'error': 'Image file not found on disk'
                }
        else:
            print("❌ No valid image path found in data structure")
            return {
                'success': False,
                'error': 'No valid image path found in data structure'
            }
            
    except Exception as e:
        error_msg = f"Error during image structure examination: {str(e)}"
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
    result = asyncio.run(examine_image_structure())
    
    print(f"\n=== Final Result ===")
    print(f"Success: {result['success']}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    if 'image_path' in result:
        print(f"Image path: {result['image_path']}")
    if 'public_url' in result:
        print(f"Public URL: {result['public_url']}")