#!/usr/bin/env python3
"""
Test ngrok access to static files
"""

import requests
import json
import os

def test_ngrok_access():
    print("=== Testing Ngrok Access ===")
    
    # Check ngrok status
    response = requests.get('http://localhost:8000/api/user-workflow/ngrok-status')
    print('Ngrok status:', response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print('Tunnels:', json.dumps(data, indent=2))
        
        # Try to access a static file directly through ngrok
        if data.get('ngrok_status', {}).get('tunnels'):
            tunnel_url = data['ngrok_status']['tunnels'][0]['public_url']
            print(f"Tunnel URL: {tunnel_url}")
            
            # List files in static/uploads
            uploads_dir = 'static/uploads'
            if os.path.exists(uploads_dir):
                files = os.listdir(uploads_dir)
                print(f"Files in {uploads_dir}: {files}")
                
                if files:
                    test_file = files[0]
                    ngrok_url = f'{tunnel_url}/static/uploads/{test_file}'
                    print(f'Testing ngrok URL: {ngrok_url}')
                    
                    # Try with GET instead of HEAD to see the actual content
                    response = requests.get(ngrok_url, allow_redirects=True, timeout=10)
                    print(f'GET Status: {response.status_code}')
                    print(f'Content-Type: {response.headers.get("content-type", "unknown")}')
                    print(f'Content length: {len(response.content)}')
                    print(f'URL after redirects: {response.url}')
                    
                    # Check if it's an image
                    if response.headers.get("content-type", "").startswith("image/"):
                        print("✓ Response is an image!")
                        return True
                    else:
                        print("✗ Response is not an image")
                        print(f"First 500 chars: {response.text[:500]}")
                        return False
                else:
                    print("No files found in uploads directory")
            else:
                print(f"Directory {uploads_dir} does not exist")
    
    return False

if __name__ == "__main__":
    success = test_ngrok_access()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")