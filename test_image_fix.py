import requests
import json

# Test the complete workflow with image generation
print('Testing complete workflow with image...')
response = requests.post('http://localhost:8000/api/user-workflow/create-content', json={
    'user_input': 'AI technology trends',
    'platforms': ['instagram'],
    'tone': 'professional',
    'include_image': True
})

if response.status_code == 200:
    result = response.json()
    session_id = result['session_id']
    print(f'Content created with session: {session_id}')
    
    # Check if public_images are available
    content = result.get('content', {})
    if 'public_images' in content and content['public_images']:
        print(f'Public images available: {len(content["public_images"])}')
        for img in content['public_images']:
            print(f'  Public URL: {img.get("public_url", "N/A")}')
    else:
        print('No public_images found in content')
        print(f'Available keys in content: {list(content.keys())}')
        # Also check if images exist that might become public
        if 'images' in content:
            print(f'Raw images available: {len(content["images"])}')
        
    # Now test publishing
    print('\nTesting publishing...')
    publish_response = requests.post('http://localhost:8000/api/user-workflow/confirm-content', json={
        'session_id': session_id,
        'confirmed': True
    })
    
    if publish_response.status_code == 200:
        publish_result = publish_response.json()
        print(f'Publishing result: {json.dumps(publish_result, indent=2)}')
    else:
        print(f'Publishing failed: {publish_response.status_code}')
        print(f'Error: {publish_response.text}')
        
else:
    print(f'Content creation failed: {response.status_code}')
    print(response.text)