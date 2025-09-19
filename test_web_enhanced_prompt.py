#!/usr/bin/env python3
"""Test script to verify enhanced prompt is working in the web interface"""

import requests
import json

def test_create_content_with_enhanced_prompt():
    """Test the create content endpoint to see if enhanced prompt is generated"""
    
    url = "http://localhost:8000/create-content"
    
    # Test data - using form data format
    data = {
        "topic": "AI in healthcare",
        "tone": "professional",
        "platforms": ["linkedin", "twitter"],  # This should be a list
        "include_image": True,
        "caption_length": "medium",
        "hashtag_count": 10
    }
    
    try:
        print("Testing create-content endpoint...")
        print(f"Sending form data: {data}")
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            # The response is HTML, so let's check if enhanced prompt is in the content
            html_content = response.text
            print(f"\nHTML Response received (length: {len(html_content)} characters)")
            
            # Check if enhanced prompt is in the HTML
            if 'Enhanced Prompt:' in html_content:
                print(f"\n✅ SUCCESS: Enhanced prompt section found in HTML response!")
                
                # Try to extract the enhanced prompt from HTML - look for the div content
                import re
                enhanced_match = re.search(r'<strong>Enhanced Prompt:</strong>\s*<div[^>]*>([^<]+)</div>', html_content, re.DOTALL)
                if enhanced_match:
                    enhanced_prompt = enhanced_match.group(1).strip()
                    print(f"Enhanced Prompt: {enhanced_prompt[:100]}...")
                    
                    if enhanced_prompt != "AI in healthcare":
                        print(f"\n✅ SUCCESS: Enhanced prompt is different from original topic!")
                        print(f"Original: AI in healthcare")
                        print(f"Enhanced: {enhanced_prompt[:100]}...")
                    else:
                        print(f"\n❌ ISSUE: Enhanced prompt is same as original topic")
                else:
                    # Try alternative pattern - look for the bg-light div
                    enhanced_match = re.search(r'<div class="bg-light p-3 rounded mt-1">\s*([^<]+)\s*</div>', html_content, re.DOTALL)
                    if enhanced_match:
                        enhanced_prompt = enhanced_match.group(1).strip()
                        print(f"Enhanced Prompt: {enhanced_prompt[:100]}...")
                        print(f"\n✅ SUCCESS: Enhanced prompt extracted successfully!")
                    else:
                        print(f"Enhanced prompt section found but couldn't extract exact text")
            else:
                print(f"\n❌ ISSUE: Enhanced prompt section not found in HTML response")
                
            # Save HTML for debugging
            with open('test_response.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML response saved to test_response.html for inspection")
            
        else:
            print(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_content_with_enhanced_prompt()