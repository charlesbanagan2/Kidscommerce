"""
Quick test for /api/v1/chat/product/start endpoint
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test login first
print("1. Logging in as buyer...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        'email': 'buyer@gmail.com',
        'password': 'Buyer123!'
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json().get('access_token')
print(f"Login successful! Token: {token[:20]}...")

# Get a product
print("\n2. Getting a product...")
products_response = requests.get(
    f"{BASE_URL}/api/v1/products",
    headers={'Authorization': f'Bearer {token}'}
)

if products_response.status_code != 200:
    print(f"Failed to get products: {products_response.text}")
    exit(1)

products = products_response.json().get('products', [])
if not products:
    print("No products found!")
    exit(1)

product_id = products[0]['id']
print(f"Using product ID: {product_id}")

# Test product chat start
print("\n3. Starting product chat...")
chat_response = requests.post(
    f"{BASE_URL}/api/v1/chat/product/start",
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'product_id': product_id,
        'message': 'Test message'
    }
)

print(f"Status: {chat_response.status_code}")
print(f"Response: {json.dumps(chat_response.json(), indent=2)}")

if chat_response.status_code == 200:
    print("\n✓ SUCCESS!")
else:
    print(f"\n✗ FAILED: {chat_response.text}")
