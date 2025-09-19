#!/usr/bin/env python3
"""
Test script to debug GetLate API accounts endpoint
"""

import requests
import json
import os
from urllib.parse import urljoin

# Load API key from environment
api_key = os.getenv('GETLATE_API_KEY', 'your-api-key-here')
base_url = "https://getlate.dev/api/v1"

def test_getlate_endpoints():
    """Test various GetLate API endpoints"""
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'GetLate-SocialMediaAutomation/1.0.0'
    }
    
    # Test different endpoint variations
    endpoints_to_test = [
        '/accounts',
        '/api/v1/accounts',
        '/v1/accounts',
        '/api/accounts'
    ]
    
    print(f"Testing GetLate API with base URL: {base_url}")
    print(f"Using API key: {api_key[:10]}...")
    print("-" * 50)
    
    for endpoint in endpoints_to_test:
        url = urljoin(base_url, endpoint.lstrip('/'))
        print(f"\nTesting endpoint: {endpoint}")
        print(f"Full URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw response: {response.text}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")
    
    # Also test what the actual API structure might be
    print("\n" + "=" * 50)
    print("Testing common API patterns...")
    
    # Test if it might be /user/accounts or /profile/accounts
    alternative_endpoints = [
        '/user/accounts',
        '/profile/accounts',
        '/connections',
        '/social-accounts',
        '/platforms'
    ]
    
    for endpoint in alternative_endpoints:
        url = urljoin(base_url, endpoint.lstrip('/'))
        print(f"\nTesting alternative endpoint: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Success! Response: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw response: {response.text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_getlate_endpoints()