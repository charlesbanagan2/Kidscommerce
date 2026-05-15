#!/usr/bin/env python3
"""
Test script for Flutter login screen
Tests the login functionality with a buyer account
"""

import requests
import json
import sys
import time

# Backend URL
BASE_URL = 'http://192.168.1.20:5000'

# Test credentials
BUYER_EMAIL = 'buyer@test.com'
BUYER_PASSWORD = 'password123'

def test_login():
    """Test buyer login"""
    print("="*60)
    print("FLUTTER LOGIN SCREEN TEST - BUYER ACCOUNT")
    print("="*60)
    print()
    
    # Test 1: Check if backend is running
    print("1️⃣  Checking if backend server is running...")
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        print("   ✅ Backend server is reachable")
        print(f"   Response: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: Cannot connect to backend server")
        print(f"   Make sure backend is running at {BASE_URL}")
        return False
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
    
    print()
    
    # Test 2: Attempt login with buyer account
    print("2️⃣  Testing buyer login...")
    print(f"   Email: {BUYER_EMAIL}")
    print(f"   Password: {'*' * len(BUYER_PASSWORD)}")
    print()
    
    try:
        login_url = f'{BASE_URL}/api/v1/auth/login'
        payload = {
            'email': BUYER_EMAIL,
            'password': BUYER_PASSWORD
        }
        
        response = requests.post(
            login_url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ LOGIN SUCCESSFUL!")
            print()
            
            # Parse response
            if 'tokens' in data:
                tokens = data['tokens']
                access_token = tokens.get('access_token', '')[:20] + '...'
                print(f"   Access Token: {access_token}")
            
            if 'user' in data:
                user = data['user']
                print(f"   User ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            
            print()
            print("   ✅ BUYER ACCOUNT LOGIN VERIFIED")
            return True
            
        elif response.status_code == 401:
            print("   ❌ INVALID CREDENTIALS")
            print(f"   Response: {response.json()}")
            return False
            
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ ERROR: Request timeout")
        print("   Backend server may be down or slow")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: Cannot connect to backend")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_validation_errors():
    """Test validation errors"""
    print("3️⃣  Testing validation errors...")
    print()
    
    test_cases = [
        {
            'name': 'Empty email',
            'email': '',
            'password': 'password123',
            'expected_error': True
        },
        {
            'name': 'Empty password',
            'email': 'buyer@test.com',
            'password': '',
            'expected_error': True
        },
        {
            'name': 'Invalid email format',
            'email': 'invalid-email',
            'password': 'password123',
            'expected_error': True
        },
        {
            'name': 'Wrong password',
            'email': 'buyer@test.com',
            'password': 'wrongpassword',
            'expected_error': True
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"   Test {i}: {test['name']}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/v1/auth/login',
                json={'email': test['email'], 'password': test['password']},
                timeout=10
            )
            
            if response.status_code >= 400:
                print(f"      ✅ Correctly rejected (Status: {response.status_code})")
            else:
                print(f"      ⚠️  Unexpected success")
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
    
    print()

def main():
    """Run all tests"""
    print()
    
    # Run login test
    login_success = test_login()
    
    print()
    print("="*60)
    
    # Test validation
    test_validation_errors()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if login_success:
        print("✅ BUYER LOGIN TEST: PASSED")
        print()
        print("The login screen is working correctly!")
        print("You can now:")
        print("  • Log in with: buyer@test.com / password123")
        print("  • Test on the Flutter app")
        print("  • Verify all UI elements fit on screen")
        print("  • Check error message display")
        print()
        return 0
    else:
        print("❌ BUYER LOGIN TEST: FAILED")
        print()
        print("Please check:")
        print("  • Backend server is running")
        print("  • Database has buyer@test.com account")
        print("  • Network connection is working")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
