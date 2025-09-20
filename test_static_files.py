#!/usr/bin/env python3
"""Test static file access through ngrok"""

import os
import requests

def test_static_files():
    # Check what files are in static/uploads
    uploads_dir = 'static/uploads'
    if not os.path.exists(uploads_dir):
        print('static/uploads directory does not exist')
        return
        
    files = os.listdir(uploads_dir)
    print('Files in static/uploads:', files)
    
    if not files:
        print('No files found in static/uploads')
        return
    
    # Test accessing a file through ngrok
    test_file = files[0]
    ngrok_url = 'https://43d3dda256d5.ngrok-free.app'
    file_url = f'{ngrok_url}/static/uploads/{test_file}'
    
    print(f'Testing access to: {file_url}')
    response = requests.get(file_url, allow_redirects=True)
    print(f'Status code: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type", "unknown")}')
    print(f'Content length: {len(response.content)} bytes')
    
    if response.status_code == 200:
        print('SUCCESS: File accessible through ngrok')
    else:
        print('FAILED: File not accessible through ngrok')
        print('Response headers:', dict(response.headers))
        
    # Also test direct localhost access
    local_url = f'http://localhost:8000/static/uploads/{test_file}'
    print(f'\\nTesting local access to: {local_url}')
    local_response = requests.get(local_url)
    print(f'Local status code: {local_response.status_code}')
    
    if local_response.status_code == 200:
        print('SUCCESS: File accessible locally')
    else:
        print('FAILED: File not accessible locally')

if __name__ == '__main__':
    test_static_files()