#!/usr/bin/env python3
"""Test API to check Order #55"""

import requests
import json
import os
from dotenv import load_dotenv

API_BASE = "http://localhost:5000/api/v1"

# Test account
EMAIL = "juanbuyer@gmail.com"
PASSWORD = "password123"

print("🔍 Testing Order #55 API Response...")
print(f"API Base: {API_BASE}")

try:
    # Step 1: Login to get token
    print("\n📝 Step 1: Logging in...")
    login_url = f"{API_BASE}/auth/login"
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, json=login_data, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        exit(1)
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Login failed: {result.get('error')}")
        exit(1)
    
    token = result.get('access_token')
    user_id = result.get('user', {}).get('id')
    print(f"✅ Logged in as {EMAIL} (ID: {user_id})")
    print(f"Token: {token[:30]}...")
    
    # Step 2: Get Order #55
    print("\n🔗 Step 2: Fetching Order #55...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_BASE}/buyer/orders/55"
    print(f"GET {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
    
    if response.status_code == 200 and result.get('success'):
        order = result.get('order', {})
        print(f"\n✅ Order #55 Details:")
        print(f"  id: {order.get('id')}")
        print(f"  status: {order.get('status')}")
        print(f"  buyer_id: {order.get('buyer_id')}")
        print(f"  rider_id: {order.get('rider_id')}")
        print(f"  rider_name: {order.get('rider_name')}")
        print(f"  rider_phone: {order.get('rider_phone')}")
        print(f"  rider_profile_picture: {order.get('rider_profile_picture')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

