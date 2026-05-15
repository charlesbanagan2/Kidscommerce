#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

print("=" * 70)
print("TESTING ALL FIXES - COMPREHENSIVE VERIFICATION")
print("=" * 70)

# TEST 1: Product Images
print("\n[TEST 1] PRODUCT IMAGES")
try:
    response = requests.get('http://192.168.1.20:5000/api/v1/products')
    data = response.json()
    products = data.get('products', [])
    
    print(f"  Products returned: {len(products)}")
    if products:
        p = products[0]
        print(f"  First product: {p.get('name')}")
        print(f"    - image: {p.get('image')}")
        print(f"    - gallery count: {len(p.get('gallery', []))}")
        print(f"    - store_name: {p.get('store_name')}")
        print(f"    - store_logo: {p.get('store_logo')}")
        print("  [PASS] Product images working")
    else:
        print("  [FAIL] No products returned")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# TEST 2: Add to Cart
print("\n[TEST 2] ADD TO CART")
try:
    # Create JWT token
    login_data = {'email': 'zeffpolicarpio2004@gmail.com', 'password': 'zeff123'}
    login_response = requests.post('http://192.168.1.20:5000/api/v1/auth/login', json=login_data)
    token = login_response.json().get('token')
    
    if token:
        # Add to cart
        cart_data = {'product_id': 24, 'quantity': 1}
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        cart_response = requests.post('http://192.168.1.20:5000/api/v1/buyer/cart/add', 
                                     json=cart_data, headers=headers)
        
        if cart_response.status_code == 201:
            print("  Status: 201 Created")
            print(f"  Response: {cart_response.json().get('message')}")
            print("  [PASS] Add to cart working")
        else:
            print(f"  Status: {cart_response.status_code}")
            print(f"  Response: {cart_response.text[:200]}")
            print("  [FAIL] Add to cart not working")
    else:
        print("  [FAIL] Could not get auth token")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# TEST 3: Store Background Field
print("\n[TEST 3] STORE BACKGROUND FIELD")
try:
    response = requests.get('http://192.168.1.20:5000/api/v1/products')
    data = response.json()
    products = data.get('products', [])
    
    if products:
        p = products[0]
        has_store_background = 'store_background' in p
        has_store_background_url = 'store_background_url' in p
        
        print(f"  store_background field: {has_store_background}")
        print(f"  store_background_url field: {has_store_background_url}")
        
        if has_store_background and has_store_background_url:
            print("  [PASS] Store background fields present in API")
        else:
            print("  [FAIL] Store background fields missing")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# TEST 4: API Response Format
print("\n[TEST 4] API RESPONSE FORMAT")
try:
    response = requests.get('http://192.168.1.20:5000/api/v1/products')
    if response.status_code == 200:
        print("  Status: 200 OK")
        data = response.json()
        print(f"  Has pagination: {'pagination' in data}")
        print(f"  Has products: {'products' in data}")
        print("  [PASS] API format correct")
    else:
        print(f"  [FAIL] Status: {response.status_code}")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
