#!/usr/bin/env python3
"""Quick test to check API responses"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test 1: Get products
print("=" * 60)
print("TEST 1: GET /api/v1/products")
print("=" * 60)
try:
    resp = requests.get(f"{BASE_URL}/api/v1/products?limit=2", timeout=5)
    print(f"Status: {resp.status_code}\n")
    
    data = resp.json()
    
    # Show structure
    print("Response structure:")
    print(f"- Keys: {list(data.keys())}")
    
    if 'products' in data:
        products = data['products']
        print(f"- Number of products: {len(products)}")
        if products:
            p = products[0]
            print(f"\nFirst product keys: {list(p.keys())}")
            print(f"First product data:")
            print(json.dumps(p, indent=2))
    else:
        print("No 'products' key in response!")
        print(f"Full response: {json.dumps(data, indent=2)[:1000]}")
        
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check auth
print("\n" + "=" * 60)
print("TEST 2: POST /api/v1/auth/login")
print("=" * 60)
try:
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "buyer@example.com", "password": "password"},
        timeout=5
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response keys: {list(data.keys())}")
    if data.get('success'):
        print("✓ Login successful")
        if 'tokens' in data:
            token = data['tokens'].get('access_token')
            print(f"Access token: {token[:30]}...")
    else:
        print(f"Login failed: {data.get('error', data)}")
except Exception as e:
    print(f"Error: {e}")
