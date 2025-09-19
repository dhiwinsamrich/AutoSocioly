#!/usr/bin/env python3
"""
Test script for enhanced image modification with core preservation
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.image_gen import ImageGenerationService

async def test_enhanced_modification():
    """Test the new enhanced image modification method"""
    print("🧪 Testing Enhanced Image Modification with Core Preservation")
    print("=" * 60)
    
    service = ImageGenerationService()
    
    try:
        # Test the new precision modification method
        result = await service.modify_image_preserving_core(
            original_prompt="A modern coffee shop interior with warm lighting, wooden furniture, and people working on laptops",
            modification_request="Add more plants and make the lighting brighter",
            platform="instagram"
        )
        
        print("✅ Enhanced modification method working successfully!")
        print(f"📸 Generated image URL: {result.get('image_url', 'No URL')[:60]}...")
        print(f"🎯 Preservation metadata: {result.get('preservation_score', 'N/A')}")
        print(f"🔧 Modification type: {result.get('modification_type', 'N/A')}")
        print(f"🎨 Generation approach: {result.get('generation_approach', 'N/A')}")
        print(f"📊 Platform: {result.get('platform', 'N/A')}")
        
        # Verify all expected metadata is present
        expected_keys = ['modification_type', 'original_prompt', 'modification_request', 
                        'preserved_elements', 'preservation_score', 'modification_precision']
        
        missing_keys = [key for key in expected_keys if key not in result]
        if missing_keys:
            print(f"⚠️  Missing metadata keys: {missing_keys}")
        else:
            print("✅ All preservation metadata present")
            
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_modification())
    sys.exit(0 if success else 1)