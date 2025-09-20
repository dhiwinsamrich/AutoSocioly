#!/usr/bin/env python3
"""
Complete Platform Integration - Demonstrates end-to-end workflow with proper authentication
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import time

# Import our services
from src.services.getlate_service import GetLateService
from src.services.auth_service import AuthService
from src.models import Platform

def get_api_key() -> str:
    """Get API key from environment"""
    return os.getenv('GETLATE_API_KEY', 'sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28')

def test_complete_workflow():
    """Test the complete workflow with proper authentication"""
    print("🚀 TESTING COMPLETE WORKFLOW WITH PROPER AUTHENTICATION")
    print("=" * 70)
    
    # Initialize services
    api_key = get_api_key()
    getlate_service = GetLateService(api_key=api_key)
    auth_service = AuthService(getlate_service)
    
    # Step 1: Create content workflow
    print("\n📋 STEP 1: Creating Content Workflow")
    print("-" * 40)
    
    create_data = {
        'topic': 'AI Technology Trends 2024',
        'platforms': 'instagram,linkedin,x,reddit',
        'tone': 'professional'
    }
    
    # Use form data as required by the endpoint
    response = requests.post(
        'http://localhost:8000/create-content',
        data=create_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Extract workflow ID from redirect URL
    workflow_id = None
    if response.history:
        final_url = response.url
        if 'workflow_id=' in final_url:
            workflow_id = final_url.split('workflow_id=')[-1].split('&')[0]
    
    if not workflow_id:
        print("❌ Could not extract workflow ID")
        return
    
    print(f"✅ Workflow created successfully!")
    print(f"🆔 Workflow ID: {workflow_id}")
    
    # Step 2: Check workflow status and generate images
    print("\n🖼️ STEP 2: Generating Images for Media Platforms")
    print("-" * 40)
    
    # Wait a moment for workflow to process
    time.sleep(2)
    
    # Check workflow status
    status_response = requests.get(f'http://localhost:8000/workflow-status/{workflow_id}')
    if status_response.status_code == 200:
        workflow_data = status_response.json()
        print(f"Workflow Status: {workflow_data.get('status', 'unknown')}")
        
        # Generate images if not already present
        if not workflow_data.get('generated_images'):
            print("🎨 Generating images...")
            
            # Create a sample image for testing
            sample_image_path = f"static/uploads/workflow_{workflow_id}_image.jpg"
            try:
                from PIL import Image
                img = Image.new('RGB', (800, 600), color='blue')
                img.save(sample_image_path)
                print(f"✅ Created sample image: {sample_image_path}")
            except ImportError:
                print("❌ PIL not available, skipping image generation")
    
    # Step 3: Prepare platform-specific data with proper authentication
    print("\n🔐 STEP 3: Preparing Platform-Specific Authentication Data")
    print("-" * 40)
    
    # Define account IDs (these would be your actual account IDs)
    account_mappings = {
        Platform.INSTAGRAM: "instagram_demo_account",
        Platform.LINKEDIN: "linkedin_demo_account", 
        Platform.X: "x_demo_account",
        Platform.REDDIT: "reddit_demo_account"
    }
    
    # Define platform-specific configurations
    platform_configs = {
        Platform.INSTAGRAM: {
            "hashtags": ["#AI", "#Technology", "#Innovation", "#2024"],
            "location": "San Francisco, CA"
        },
        Platform.LINKEDIN: {
            "visibility": "public",
            "article_url": "https://example.com/ai-trends-2024"
        },
        Platform.X: {
            "hashtags": ["#AI", "#Technology", "#Future"],
            "mentions": ["@techhandle", "@ainews"]
        },
        Platform.REDDIT: {
            "subreddit": "technology",
            "url": "https://example.com/ai-trends-2024"
        }
    }
    
    # Create public URLs for images using ngrok
    print("🌐 Creating public image URLs...")
    image_paths = [f"static/uploads/workflow_{workflow_id}_image.jpg"]
    public_urls = auth_service.make_public_media_urls(image_paths)
    
    if public_urls:
        print(f"✅ Public URL created: {public_urls[0]}")
    else:
        print("❌ Failed to create public URLs, using local paths")
        public_urls = [f"http://localhost:8000/static/uploads/workflow_{workflow_id}_image.jpg"]
    
    # Step 4: Test posting to platforms with proper authentication
    print("\n📤 STEP 4: Testing Platform Posting with Authentication")
    print("-" * 40)
    
    content = "🚀 AI Technology Trends 2024: Discover the latest innovations shaping our future! #AI #Technology #Innovation"
    
    # Test each platform individually
    platforms_to_test = [Platform.INSTAGRAM, Platform.LINKEDIN, Platform.X, Platform.REDDIT]
    
    for platform in platforms_to_test:
        print(f"\n📱 Testing {platform.value.title()}...")
        
        # Create authenticated post data
        post_data = auth_service.create_authenticated_post_data(
            content=content,
            platforms=[platform],
            account_mappings=account_mappings,
            platform_configs=platform_configs,
            media_urls=public_urls if platform in [Platform.INSTAGRAM] else None
        )
        
        # Validate platform requirements
        validation = auth_service.validate_platform_requirements(
            platform=platform,
            content=content,
            media_urls=public_urls if platform in [Platform.INSTAGRAM] else None,
            platform_config=platform_configs.get(platform)
        )
        
        if validation['valid']:
            print(f"✅ {platform.value.title()} validation passed")
            
            # Test with the publish-content endpoint
            publish_data = {
                'workflow_id': workflow_id,
                f'selected_variants[{platform.value}]': content
            }
            
            response = requests.post(
                'http://localhost:8000/publish-content',
                data=publish_data
            )
            
            if response.status_code == 200:
                print(f"✅ {platform.value.title()} post successful!")
            else:
                print(f"❌ {platform.value.title()} post failed: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ {platform.value.title()} validation failed:")
            print(f"   Errors: {validation.get('errors', [])}")
            print(f"   Warnings: {validation.get('warnings', [])}")
    
    # Step 5: Test batch posting with GetLate API
    print("\n🌟 STEP 5: Testing Batch Posting with GetLate API")
    print("-" * 40)
    
    # Create batch post data for multiple platforms
    batch_post_data = auth_service.create_authenticated_post_data(
        content=content,
        platforms=platforms_to_test,
        account_mappings=account_mappings,
        platform_configs=platform_configs,
        media_urls=public_urls if any(p in [Platform.INSTAGRAM] for p in platforms_to_test) else None
    )
    
    print("📋 Batch Post Data:")
    print(json.dumps(batch_post_data, indent=2))
    
    # Test with GetLate API
    print("\n🚀 Testing GetLate API batch posting...")
    
    try:
        response = requests.post(
            'https://getlate.dev/api/v1/posts',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json=batch_post_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch posting successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Batch posting failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API request failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"  - Workflow ID: {workflow_id}")
    print(f"  - Platforms Tested: {len(platforms_to_test)}")
    print(f"  - Authentication: Bearer token format")
    print(f"  - Image URLs: {len(public_urls)} public URLs created")
    print("\n💡 Key Features Demonstrated:")
    print("  - Proper Bearer token authentication")
    print("  - Platform-specific account configuration")
    print("  - Media URL generation with ngrok")
    print("  - Batch posting to multiple platforms")
    print("  - Validation and error handling")

if __name__ == "__main__":
    test_complete_workflow()