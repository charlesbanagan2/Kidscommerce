#!/usr/bin/env python3
"""
Complete test to debug all issues:
1. Check products API response
2. Get valid buyer token
3. Test Add to Cart endpoint
4. Check store background/logo
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

print("="*70)
print("COMPREHENSIVE API TEST")
print("="*70)

# First check what users exist
print("\n1. Checking database for test accounts...")
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')
from app import app, db, User

with app.app_context():
    buyers = User.query.filter_by(role='buyer').limit(5).all()
    print(f"Found {len(buyers)} buyer accounts:")
    for u in buyers[:5]:
        print(f"  - ID: {u.id}, Email: {u.email}, First: {u.first_name}, Last: {u.last_name}")

# Test 2: Get products with proper analysis
print("\n2. Testing GET /api/v1/products...")
try:
    resp = requests.get(f"{BASE_URL}/api/v1/products?limit=1", timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('products'):
            p = data['products'][0]
            print(f"✓ Product API working")
            print(f"  - Image: {p.get('image')}")
            print(f"  - Gallery count: {len(p.get('gallery', []))}")
            print(f"  - Store name: {p.get('store_name')}")
            print(f"  - Store logo: {p.get('store_logo')}")
    else:
        print(f"✗ Status: {resp.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Login and get token
print("\n3. Testing POST /api/v1/auth/login with first buyer...")
token = None
try:
    with app.app_context():
        buyer = User.query.filter_by(role='buyer').first()
        if buyer:
            resp = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"email": buyer.email, "password": buyer.password},
                timeout=5
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success') or data.get('tokens'):
                    tokens = data.get('tokens', {})
                    token = tokens.get('access_token')
                    if token:
                        print(f"✓ Login successful")
                        print(f"  - Token: {token[:30]}...")
                    else:
                        print(f"Response: {data}")
                else:
                    print(f"✗ {data}")
            else:
                print(f"Response: {resp.text}")
        else:
            print("No buyer found")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Add to Cart with token
if token:
    print("\n4. Testing POST /api/v1/buyer/cart/add...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "product_id": 24,
            "quantity": 1,
            "size": "M",
            "color": "blue"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/buyer/cart/add",
            json=payload,
            headers=headers,
            timeout=5
        )
        print(f"Status: {resp.status_code}")
        data = resp.json()
        if resp.status_code in [200, 201]:
            print(f"✓ Add to cart successful")
            print(f"  Response: {json.dumps(data, indent=2)[:300]}")
        else:
            print(f"✗ Failed: {data}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("\n4. Skipping Add to Cart test (no token)")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
