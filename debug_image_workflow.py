#!/usr/bin/env python3
"""
Debug script to trace the image workflow step by step
"""

import asyncio
import json
import requests
from datetime import datetime

def test_create_content():
    """Test content creation with image"""
    print("=== Testing Content Creation ===")
    
    url = "http://localhost:8000/api/create-content"
    payload = {
        "prompt": "Create a beautiful sunset over mountains with inspirational text about success",
        "platforms": ["linkedin"],
        "include_image": True,
        "image_style": "photorealistic"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Session ID: {data.get('session_id')}")
        print(f"Content: {json.dumps(data.get('content'), indent=2)}")
        
        # Check for images
        content = data.get('content', {})
        if 'images' in content:
            print(f"Images found: {len(content['images'])}")
            for i, img in enumerate(content['images']):
                print(f"  Image {i+1}: {img}")
        else:
            print("No 'images' key found in content")
            
        if 'public_images' in content:
            print(f"Public images found: {len(content['public_images'])}")
            for i, img in enumerate(content['public_images']):
                print(f"  Public Image {i+1}: {img}")
        else:
            print("No 'public_images' key found in content")
            
        return data.get('session_id')
    else:
        print(f"Error: {response.text}")
        return None

def test_confirm_and_post(session_id):
    """Test confirming and posting content"""
    print(f"\n=== Testing Confirm and Post (Session: {session_id}) ===")
    
    url = f"http://localhost:8000/api/confirm-content/{session_id}"
    payload = {
        "user_confirmation": True,
        "confirmed": True
    }
    
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check what content was posted
        results = data.get('results', {})
        for platform, result in results.items():
            print(f"\nPlatform: {platform}")
            print(f"  Success: {result.get('success')}")
            print(f"  Content: {result.get('content')}")
            print(f"  Media URLs: {result.get('media_urls')}")
    else:
        print(f"Error: {response.text}")

def test_static_file_access():
    """Test if static files are accessible"""
    print("\n=== Testing Static File Access ===")
    
    # List files in static/uploads
    import os
    uploads_dir = "static/uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"Files in {uploads_dir}: {files}")
        
        if files:
            # Test local access
            test_file = files[0]
            local_url = f"http://localhost:8000/static/uploads/{test_file}"
            print(f"Testing local access: {local_url}")
            
            try:
                response = requests.head(local_url, timeout=5)
                print(f"Local access status: {response.status_code}")
            except Exception as e:
                print(f"Local access failed: {e}")
            
            # Test ngrok access
            try:
                # Get ngrok tunnel info
                tunnel_response = requests.get("http://localhost:8000/api/ngrok-status")
                if tunnel_response.status_code == 200:
                    tunnel_data = tunnel_response.json()
                    if tunnel_data.get('tunnels'):
                        tunnel_url = tunnel_data['tunnels'][0]['public_url']
                        ngrok_url = f"{tunnel_url}/static/uploads/{test_file}"
                        print(f"Testing ngrok access: {ngrok_url}")
                        
                        response = requests.head(ngrok_url, timeout=10)
                        print(f"Ngrok access status: {response.status_code}")
                    else:
                        print("No ngrok tunnels found")
                else:
                    print("Could not get ngrok status")
            except Exception as e:
                print(f"Ngrok access test failed: {e}")
    else:
        print(f"Directory {uploads_dir} does not exist")

if __name__ == "__main__":
    print(f"Starting debug test at {datetime.now()}")
    
    # Test static file access first
    test_static_file_access()
    
    # Test full workflow
    session_id = test_create_content()
    if session_id:
        test_confirm_and_post(session_id)
    
    print(f"\n=== Debug Test Complete ===")