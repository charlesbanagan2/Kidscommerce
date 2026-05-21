#!/usr/bin/env python3
"""Test that product 32 can now be added to cart"""
import requests
import json

BASE_URL = "http://192.168.1.4:5000"

print("=" * 60)
print("Testing Cart Fix for Product ID 32")
print("=" * 60)

# Step 1: Login to get token
print("\n1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "email": "buyer@test.com",  # Change to your test buyer email
        "password": "test123"        # Change to your test password
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    print("\nPlease update the email/password in the script")
    exit(1)

token = login_response.json().get('token')
print(f"✓ Login successful, got token")

# Step 2: Try to add product 32 to cart
print("\n2. Adding Product ID 32 to cart...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

cart_response = requests.post(
    f"{BASE_URL}/api/v1/buyer/cart",
    json={
        "product_id": 32,
        "quantity": 1
    },
    headers=headers
)

print(f"Status Code: {cart_response.status_code}")
print(f"Response: {json.dumps(cart_response.json(), indent=2)}")

if cart_response.status_code == 201:
    print("\n✅ SUCCESS! Product 32 can now be added to cart!")
    print("The fix is working correctly.")
elif cart_response.status_code == 404:
    print("\n❌ Still getting 404 error")
    print("The server may need to be restarted for changes to take effect")
else:
    print(f"\n⚠️ Unexpected status code: {cart_response.status_code}")

print("\n" + "=" * 60)
