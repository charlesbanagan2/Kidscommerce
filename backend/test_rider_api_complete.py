#!/usr/bin/env python3
"""
Test script for Rider Mobile API endpoints
Run this AFTER restarting the Flask backend server
"""

import requests
import json

BASE_URL = "http://192.168.1.20:5000"

# Test credentials (use your actual rider credentials)
RIDER_EMAIL = "juanrider@gmail.com"
RIDER_PASSWORD = "password123"  # Update with actual password

def test_login():
    """Test rider login"""
    print("\n" + "="*60)
    print("TEST 1: Rider Login")
    print("="*60)
    
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": RIDER_EMAIL,
        "password": RIDER_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"\n✅ Login successful! Token: {token[:50]}...")
            return token
        else:
            print(f"\n❌ Login failed!")
            return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def test_available_orders(token):
    """Test getting available orders"""
    print("\n" + "="*60)
    print("TEST 2: Get Available Orders")
    print("="*60)
    
    url = f"{BASE_URL}/api/v1/rider/available-orders"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ Available orders fetched successfully!")
            print(f"   Found {data.get('count', 0)} orders")
            return True
        else:
            print(f"Response: {response.text[:500]}")
            print(f"\n❌ Failed to fetch available orders!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_earnings(token):
    """Test getting rider earnings"""
    print("\n" + "="*60)
    print("TEST 3: Get Rider Earnings")
    print("="*60)
    
    url = f"{BASE_URL}/api/v1/rider/earnings"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ Earnings fetched successfully!")
            return True
        else:
            print(f"Response: {response.text[:500]}")
            print(f"\n❌ Failed to fetch earnings!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_my_deliveries(token):
    """Test getting rider's deliveries"""
    print("\n" + "="*60)
    print("TEST 4: Get My Deliveries")
    print("="*60)
    
    url = f"{BASE_URL}/api/v1/rider/my-deliveries"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ Deliveries fetched successfully!")
            print(f"   Found {data.get('count', 0)} deliveries")
            return True
        else:
            print(f"Response: {response.text[:500]}")
            print(f"\n❌ Failed to fetch deliveries!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_profile(token):
    """Test getting rider profile"""
    print("\n" + "="*60)
    print("TEST 5: Get Rider Profile")
    print("="*60)
    
    url = f"{BASE_URL}/api/v1/rider/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ Profile fetched successfully!")
            return True
        else:
            print(f"Response: {response.text[:500]}")
            print(f"\n❌ Failed to fetch profile!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("RIDER MOBILE API TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Rider Email: {RIDER_EMAIL}")
    print("="*60)
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without valid token!")
        return
    
    # Test all endpoints
    results = []
    results.append(("Login", True))
    results.append(("Available Orders", test_available_orders(token)))
    results.append(("Earnings", test_earnings(token)))
    results.append(("My Deliveries", test_my_deliveries(token)))
    results.append(("Profile", test_profile(token)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*60)

if __name__ == "__main__":
    main()
