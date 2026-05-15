#!/usr/bin/env python3
"""Better test for Add to Cart"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("="*70)
print("TESTING ADD TO CART WITH BETTER ERROR HANDLING")
print("="*70)

# Get a valid token first
import sys
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')
from app import app, User, generate_tokens

with app.app_context():
    buyer = User.query.filter_by(role='buyer').first()
    if buyer:
        tokens = generate_tokens(buyer.id, buyer.role)
        token = tokens['access_token']
        print(f"\n1. Generated token for {buyer.email}")
        print(f"   Token: {token[:30]}...\n")
        
        # Test Add to Cart
        print("2. Testing POST /api/v1/buyer/cart/add...")
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
        
        print(f"   Status: {resp.status_code}")
        print(f"   Headers: {dict(resp.headers)}")
        print(f"   Raw body: {resp.text[:500]}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"\n   ✓ Response JSON:")
                print(json.dumps(data, indent=4))
            except:
                print(f"\n   ✗ Cannot parse JSON response")
        else:
            print(f"\n   Status is not 200, trying to parse anyway...")
            try:
                data = resp.json()
                print(json.dumps(data, indent=4))
            except:
                print(f"   Cannot parse JSON")
