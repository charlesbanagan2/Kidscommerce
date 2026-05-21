"""
Test script to verify email duplicate checking for pending users
Run this after starting the backend server
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"  # Change if your backend runs on different port
TEST_EMAIL = "test_pending_user@gmail.com"

def test_check_email_pending():
    """Test the /api/check-email endpoint with a pending user"""
    print("\n" + "="*60)
    print("TEST: Check Email with Pending Status")
    print("="*60)
    
    url = f"{BASE_URL}/api/check-email"
    payload = {"email": TEST_EMAIL}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        print(f"\nRequest: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(data, indent=2)}")
        
        # Check if response indicates pending status
        if data.get('ok') == False:
            message = data.get('message', '')
            status = data.get('status', '')
            
            if status == 'pending' or 'waiting' in message.lower() or 'approval' in message.lower():
                print("\n✅ SUCCESS: Email correctly identified as pending!")
                print(f"   Message: {message}")
                return True
            elif 'already registered' in message.lower():
                print("\n⚠️  WARNING: Email identified as registered but not specifically as pending")
                print(f"   Message: {message}")
                return False
            else:
                print("\n❌ FAILED: Unexpected response")
                print(f"   Message: {message}")
                return False
        else:
            print("\n✅ Email is available (no pending user found)")
            return True
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print(f"   Make sure the server is running at {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_register_duplicate_pending():
    """Test the /api/register endpoint with a pending email"""
    print("\n" + "="*60)
    print("TEST: Register with Pending Email")
    print("="*60)
    
    url = f"{BASE_URL}/api/register"
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": TEST_EMAIL,
        "phone": "09123456789",
        "password": "TestPassword123!",
        "role": "buyer",
        "street_address": "123 Test St",
        "barangay": "Test Barangay",
        "city": "Test City",
        "province": "Test Province",
        "region": "Test Region",
        "address": "123 Test St, Test Barangay, Test City, Test Province, Test Region"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        print(f"\nRequest: POST {url}")
        print(f"Payload: {json.dumps({**payload, 'password': '***HIDDEN***'}, indent=2)}")
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(data, indent=2)}")
        
        # Check if registration was blocked
        if response.status_code == 409:  # Conflict
            error_msg = data.get('error', '')
            
            if 'waiting' in error_msg.lower() or 'approval' in error_msg.lower() or 'pending' in error_msg.lower():
                print("\n✅ SUCCESS: Registration correctly blocked for pending email!")
                print(f"   Error: {error_msg}")
                return True
            elif 'already registered' in error_msg.lower():
                print("\n⚠️  WARNING: Registration blocked but not specifically for pending status")
                print(f"   Error: {error_msg}")
                return False
            else:
                print("\n❌ FAILED: Registration blocked with unexpected message")
                print(f"   Error: {error_msg}")
                return False
        elif response.status_code == 200:
            print("\n❌ FAILED: Registration succeeded when it should have been blocked!")
            return False
        else:
            print(f"\n⚠️  WARNING: Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print(f"   Make sure the server is running at {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def check_database_for_duplicates():
    """Instructions for checking database"""
    print("\n" + "="*60)
    print("DATABASE CHECK INSTRUCTIONS")
    print("="*60)
    print("\nTo check for duplicate emails in your database, run this SQL query:")
    print("\n" + "-"*60)
    print("""
SELECT email, COUNT(*) as count, 
       STRING_AGG(status, ', ') as statuses,
       STRING_AGG(CAST(id AS TEXT), ', ') as user_ids
FROM "user"
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY count DESC;
    """)
    print("-"*60)
    print("\nTo view all pending registrations:")
    print("\n" + "-"*60)
    print("""
SELECT id, email, first_name, last_name, role, status, created_at
FROM "user"
WHERE status = 'pending'
ORDER BY created_at DESC;
    """)
    print("-"*60)

def main():
    print("\n" + "="*60)
    print("EMAIL DUPLICATE CHECK TEST SUITE")
    print("Testing Pending User Registration Prevention")
    print("="*60)
    
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    
    print("\n⚠️  PREREQUISITES:")
    print("   1. Backend server must be running")
    print("   2. Database must have a user with email:", TEST_EMAIL)
    print("   3. That user must have status = 'pending'")
    print("\n   If you don't have a pending user, create one first!")
    
    input("\nPress ENTER to continue with tests...")
    
    # Run tests
    results = []
    
    # Test 1: Check email endpoint
    results.append(("Check Email API", test_check_email_pending()))
    
    # Test 2: Register endpoint
    results.append(("Register API", test_register_duplicate_pending()))
    
    # Show database check instructions
    check_database_for_duplicates()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The duplicate prevention is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
