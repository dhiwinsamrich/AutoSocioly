#!/usr/bin/env python3
"""
Diagnostic script to analyze account connection status and fix connection detection logic.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.getlate_service import GetLateService
from src.models import Platform

def analyze_account_connection(account_data: Dict[str, Any]) -> bool:
    """
    Analyze if an account is connected based on the API response data.
    
    Args:
        account_data: Raw account data from GetLate API
        
    Returns:
        True if account is connected, False otherwise
    """
    # Check for connection indicators
    connection_indicators = [
        # Has access token
        'accessToken' in account_data,
        # Has refresh token  
        'refreshToken' in account_data,
        # Has valid permissions
        'permissions' in account_data and len(account_data.get('permissions', [])) > 0,
        # Has platform user ID
        'platformUserId' in account_data,
        # Has connection timestamp
        'connectedAt' in account_data,
        # Has token expiration (indicates active connection)
        'tokenExpiresAt' in account_data,
        # Has username (basic requirement)
        'username' in account_data,
        # Platform-specific connection data
        'connection' in account_data and isinstance(account_data.get('connection'), dict)
    ]
    
    # Count how many indicators are present
    indicator_count = sum(connection_indicators)
    
    print(f"  Connection indicators found: {indicator_count}/8")
    print(f"    - Has access token: {'accessToken' in account_data}")
    print(f"    - Has refresh token: {'refreshToken' in account_data}")
    print(f"    - Has permissions: {'permissions' in account_data and len(account_data.get('permissions', [])) > 0}")
    print(f"    - Has platform user ID: {'platformUserId' in account_data}")
    print(f"    - Has connection timestamp: {'connectedAt' in account_data}")
    print(f"    - Has token expiration: {'tokenExpiresAt' in account_data}")
    print(f"    - Has username: {'username' in account_data}")
    print(f"    - Has connection data: {'connection' in account_data and isinstance(account_data.get('connection'), dict)}")
    
    # Consider connected if at least 4 indicators are present
    # This is a reasonable threshold for a valid connection
    return indicator_count >= 4

def main():
    """Main diagnostic function"""
    print("🔍 GetLate Account Connection Diagnostic")
    print("=" * 50)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GETLATE_API_KEY")
    if not api_key:
        print("❌ GETLATE_API_KEY not found in environment or .env file")
        return False
    
    try:
        # Initialize service
        service = GetLateService(api_key)
        
        # Get accounts from API
        print("📡 Fetching accounts from GetLate API...")
        accounts = service.get_accounts()
        
        print(f"\n📊 Found {len(accounts)} accounts in system")
        
        # Test direct API call to see raw data
        print("\n🔧 Testing direct API connection...")
        import requests
        response = requests.get(
            'https://getlate.dev/api/v1/accounts',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        if response.status_code == 200:
            raw_data = response.json()
            print("✅ Direct API call successful")
            
            # Extract accounts from response
            if isinstance(raw_data, dict):
                if 'data' in raw_data:
                    raw_accounts = raw_data['data']
                elif 'accounts' in raw_data:
                    raw_accounts = raw_data['accounts']
                else:
                    raw_accounts = raw_data.get('data', [])
            elif isinstance(raw_data, list):
                raw_accounts = raw_data
            else:
                raw_accounts = []
            
            print(f"📋 Raw API returned {len(raw_accounts)} accounts")
            
            # Analyze each account
            for i, account_data in enumerate(raw_accounts):
                print(f"\n🔍 Analyzing Account {i+1}:")
                print(f"  Platform: {account_data.get('platform', 'unknown')}")
                print(f"  Username: {account_data.get('username', 'unknown')}")
                
                # Analyze connection status
                is_connected = analyze_account_connection(account_data)
                print(f"  ✅ Connected: {is_connected}")
                
                # Show what our system sees
                if i < len(accounts):
                    system_account = accounts[i]
                    print(f"  🖥️  System sees: connected={system_account.connected}")
                    
                    if is_connected != system_account.connected:
                        print(f"  ⚠️  MISMATCH: API shows connected but system shows disconnected!")
        
        else:
            print(f"❌ Direct API call failed: {response.status_code} - {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅' if success else '❌'} Diagnostic {'completed successfully' if success else 'failed'}")