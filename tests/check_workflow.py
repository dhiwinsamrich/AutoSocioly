#!/usr/bin/env python3
"""Check workflow data and test image generation"""

import requests
import json

def check_workflow(workflow_id):
    """Check current workflow data"""
    print(f"🔍 Checking workflow: {workflow_id}")
    
    try:
        response = requests.get(f"http://localhost:8000/workflow-status/{workflow_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Status: {result.get('status', 'unknown')}")
            
            if 'workflow' in result:
                workflow = result['workflow']
                print(f"Generated images: {len(workflow.get('generated_images', []))}")
                print(f"Image ideas: {len(workflow.get('image_ideas', []))}")
                images = workflow.get('generated_images', [])
                if images:
                    print(f"First image URL: {images[0]}")
                else:
                    print("No generated images found")
            else:
                print(f"Available keys: {list(result.keys())}")
        else:
            print(f"Error: {response.text[:300]}")
            
    except Exception as e:
        print(f"Error checking workflow: {e}")

def test_image_generation(workflow_id):
    """Test image generation for the workflow"""
    print(f"\n🖼️ Testing image generation for workflow: {workflow_id}")
    
    try:
        # Test regenerate image endpoint
        data = {
            "workflow_id": workflow_id,
            "prompt": "Modern coffee shop workspace with AI technology elements",
            "original_image_url": ""
        }
        
        response = requests.post(
            "http://localhost:8000/regenerate-image",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Image generation status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"New image URL: {result.get('image_url', 'None')}")
            return result.get('image_url')
        else:
            print(f"Error: {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

if __name__ == "__main__":
    # Use the workflow ID from our test
    workflow_id = 'cc527420-f9d6-425a-9d2b-c3ba1e05d643'
    
    check_workflow(workflow_id)
    new_image_url = test_image_generation(workflow_id)
    
    if new_image_url:
        print(f"\n✅ Image generated successfully: {new_image_url}")
        print("You can now try posting to Instagram!")
    else:
        print("\n❌ Image generation failed")