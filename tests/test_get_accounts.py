#!/usr/bin/env python3
"""Test GetLate API accounts to see what's available"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.getlate_service import GetLateService
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_get_accounts():
    """Test getting accounts from GetLate API"""
    
    # Get API key from environment
    api_key = os.getenv('GETLATE_API_KEY', 'sk_e03fafd73001906ea5d35a0eea427143e02d2553cd6034130e189657427cfd28')
    
    # Initialize service
    service = GetLateService(api_key=api_key)
    
    try:
        print("=== Fetching Connected Accounts ===")
        
        accounts = service.get_accounts()
        print(f"✅ Successfully retrieved {len(accounts)} accounts")
        
        print("\n=== Account Details ===")
        for i, account in enumerate(accounts):
            print(f"\nAccount {i+1}:")
            print(f"  Platform: {account.platform}")
            print(f"  Username: {account.username}")
            print(f"  Name: {account.name}")
            print(f"  ID: {account.id}")
            print(f"  Connected: {account.connected}")
            print(f"  Permissions: {account.permissions}")
            print(f"  Access Token: {'Yes' if account.access_token else 'No'}")
            print(f"  Refresh Token: {'Yes' if account.refresh_token else 'No'}")
        
        # Check which platforms are connected
        connected_platforms = [acc.platform for acc in accounts if acc.connected]
        print(f"\n=== Connected Platforms ===")
        print(f"Connected platforms: {connected_platforms}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Account test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"Message: {e.message}")
        return False

if __name__ == "__main__":
    success = test_get_accounts()
    if success:
        print("\n🎉 Account retrieval test completed!")
    else:
        print("\n❌ Account retrieval test failed.")