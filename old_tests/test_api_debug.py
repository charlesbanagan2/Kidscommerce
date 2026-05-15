#!/usr/bin/env python3
"""
Enhanced API Testing - Debug Login Issues
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://192.168.1.20:5000"
HEADERS = {"Content-Type": "application/json"}

def test_login_detailed():
    """Test login with detailed error response"""
    print("\n=== DETAILED LOGIN TEST ===\n")
    
    credentials = [
        {"email": "buyer@example.com", "password": "password123"},
        {"email": "buyer1@example.com", "password": "password123"},
        {"email": "test@example.com", "password": "password123"},
    ]
    
    for cred in credentials:
        try:
            print(f"Testing with: {cred['email']}")
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=cred,
                headers=HEADERS,
                timeout=10
            )
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("  ✅ Login successful!")
                print(f"  Data: {json.dumps(response.json(), indent=2)[:300]}")
            else:
                print("  ❌ Login failed")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}\n")

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    print("\n=== PUBLIC ENDPOINTS TEST ===\n")
    
    endpoints = [
        ("/api/v1/products/sync", "GET", None),
        ("/api/v1/categories", "GET", None),
        ("/api/v1/sellers", "GET", None),
    ]
    
    for endpoint, method, data in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"Testing: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, headers=HEADERS, timeout=10)
            else:
                response = requests.post(url, json=data, headers=HEADERS, timeout=10)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  ✅ Success - {len(data)} items")
                elif isinstance(data, dict):
                    count = data.get('count', len(data))
                    print(f"  ✅ Success - {count} items/records")
                else:
                    print(f"  ✅ Success")
            else:
                print(f"  ❌ Failed - {response.text[:100]}")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}\n")

def test_protected_endpoints():
    """Test protected endpoints without auth to see error responses"""
    print("\n=== PROTECTED ENDPOINTS (NO AUTH) ===\n")
    
    endpoints = [
        ("/api/v1/buyer/cart", "GET"),
        ("/api/v1/buyer/orders", "GET"),
        ("/api/v1/buyer/addresses", "GET"),
    ]
    
    for endpoint, method in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"Testing: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, headers=HEADERS, timeout=10)
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:150]}")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}\n")

def check_server():
    """Check if server is running"""
    print("\n=== SERVER STATUS CHECK ===\n")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Server is not responding: {e}")

def main():
    check_server()
    test_public_endpoints()
    test_login_detailed()
    test_protected_endpoints()

if __name__ == "__main__":
    main()
