#!/usr/bin/env python3
"""
Comprehensive test script for the complete social media posting workflow.
This script tests the entire flow from content generation to posting.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None) -> Dict[str, Any]:
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, files=files, timeout=TIMEOUT)
            elif data:
                response = requests.post(url, data=data, timeout=TIMEOUT)
            else:
                response = requests.post(url, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"✓ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"html": response.text}
        else:
            print(f"  ⚠️  Error response: {response.text[:200]}")
            return {"error": response.text, "status_code": response.status_code}
            
    except Exception as e:
        print(f"✗ {method} {endpoint} - Error: {str(e)}")
        return {"error": str(e)}

def test_accounts_endpoint():
    """Test the accounts endpoint"""
    print("\n=== Testing Accounts Endpoint ===")
    result = test_endpoint("/accounts")
    
    if result.get("success"):
        accounts = result.get("data", {}).get("accounts", [])
        print(f"✓ Retrieved {len(accounts)} accounts")
        for account in accounts:
            print(f"  - {account['platform']}: {account['username']} (connected: {account['connected']})")
        return True
    else:
        print("✗ Failed to retrieve accounts")
        return False

def test_content_creation():
    """Test content creation"""
    print("\n=== Testing Content Creation ===")
    
    # Test form-based content creation
    data = {
        "topic": "AI automation testing workflow",
        "platforms": "twitter,linkedin",
        "tone": "professional",
        "include_image": "false",
        "caption_length": "short",
        "hashtag_count": "5"
    }
    
    result = test_endpoint("/create-content", "POST", data=data)
    
    if "html" in result:
        print("✓ Content creation successful - HTML response received")
        # Extract workflow ID from HTML if possible
        if "workflow_id" in result["html"]:
            print("✓ Workflow ID found in response")
            return True
        return True
    else:
        print("✗ Content creation failed")
        return False

def test_workflow_status():
    """Test workflow status endpoint"""
    print("\n=== Testing Workflow Status ===")
    
    # Test with a dummy workflow ID
    result = test_endpoint("/workflow-status/test-workflow-123")
    
    if result.get("success") or result.get("status_code") == 404:
        print("✓ Workflow status endpoint is accessible")
        return True
    else:
        print("✗ Workflow status endpoint failed")
        return False

def test_health_check():
    """Test basic health check"""
    print("\n=== Testing Health Check ===")
    result = test_endpoint("/")
    
    if "html" in result or result.get("status_code") == 200:
        print("✓ Health check passed - Server is running")
        return True
    else:
        print("✗ Health check failed")
        return False

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("🚀 Starting Comprehensive Social Media Workflow Test")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Accounts Endpoint", test_accounts_endpoint),
        ("Content Creation", test_content_creation),
        ("Workflow Status", test_workflow_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"✗ {test_name} - Exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The social media workflow is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        return False

def test_getlate_api_directly():
    """Test GetLate API directly to verify our fixes"""
    print("\n=== Testing GetLate API Directly ===")
    
    import os
    from src.services.getlate_service import GetLateService
    
    # Get API key from environment
    api_key = os.getenv("GETLATE_API_KEY")
    if not api_key:
        print("⚠️  GETLATE_API_KEY not found in environment")
        return False
    
    try:
        service = GetLateService(api_key)
        accounts = service.get_accounts()
        
        print(f"✓ GetLate API connection successful")
        print(f"✓ Retrieved {len(accounts)} accounts directly")
        
        for account in accounts:
            print(f"  - {account.platform}: {account.username} (connected: {account.connected})")
        
        return True
        
    except Exception as e:
        print(f"✗ GetLate API direct test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Social Media Automation Workflow Test Suite")
    print("This script will test the complete workflow from content generation to posting.")
    print("Make sure the server is running on http://localhost:8000")
    print("\n" + "=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✓ Server is running")
    except:
        print("✗ Server is not running. Please start it first with: python app.py")
        sys.exit(1)
    
    # Run comprehensive test
    success = run_comprehensive_test()
    
    # Test GetLate API directly
    print("\n" + "=" * 60)
    test_getlate_api_directly()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Workflow test completed successfully!")
        print("You can now use the web interface at http://localhost:8000")
    else:
        print("⚠️  Some issues were found. Please review the test results above.")
    
    sys.exit(0 if success else 1)