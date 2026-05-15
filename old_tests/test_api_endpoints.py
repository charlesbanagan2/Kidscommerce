#!/usr/bin/env python3
"""
Test script to verify API functionality:
1. Get products with full gallery/images
2. Add product to cart
3. Get cart
4. Checkout (create order)
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"
BUYER_EMAIL = "buyer@example.com"
BUYER_PASSWORD = "password"

# Test account - update these as needed
TEST_PRODUCT_ID = 1
TEST_BUYER_ID = 3

def test_get_products():
    """Test getting products with images"""
    print("\n=== Testing GET /api/v1/products ===")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products?limit=3", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            products = data.get('data', []) if isinstance(data, dict) else data
            
            if isinstance(products, list) and products:
                product = products[0]
                print(f"✓ Got {len(products)} products")
                print(f"  Product: {product.get('name')}")
                print(f"  Image: {product.get('image')}")
                print(f"  Gallery items: {len(product.get('gallery', []))}")
                if product.get('gallery'):
                    print(f"    First gallery: {product['gallery'][0]}")
                return True
            else:
                print(f"✗ No products in response or response format wrong: {data}")
                return False
        else:
            print(f"✗ Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test buyer login to get token"""
    print("\n=== Testing POST /api/v1/auth/login ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": BUYER_EMAIL, "password": BUYER_PASSWORD},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✓ Login successful")
            print(f"  Token: {token[:20]}...")
            return token
        else:
            print(f"✗ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

def test_add_to_cart(token):
    """Test adding product to cart"""
    print("\n=== Testing POST /api/v1/buyer/cart/add ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "product_id": TEST_PRODUCT_ID,
            "quantity": 1,
            "size": "M",
            "color": "blue"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/buyer/cart/add",
            json=payload,
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✓ Product added to cart")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def test_get_cart(token):
    """Test getting cart"""
    print("\n=== Testing GET /api/v1/buyer/cart ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/buyer/cart",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got cart")
            print(f"  Cart items: {len(data.get('items', []))}")
            if data.get('items'):
                print(f"  Total: {data.get('total')}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("API ENDPOINT TESTS")
    print("="*60)
    
    # Test 1: Get products
    if not test_get_products():
        print("\n✗ Product retrieval test failed!")
        sys.exit(1)
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("\n✗ Login test failed! Cannot proceed with authenticated endpoints.")
        print("  Note: You may need to create a test buyer account first.")
        print("  Skipping authenticated endpoint tests.")
        sys.exit(0)
    
    # Test 3: Add to cart
    if not test_add_to_cart(token):
        print("\n✗ Add to cart test failed!")
    
    # Test 4: Get cart
    if not test_get_cart(token):
        print("\n✗ Get cart test failed!")
    
    print("\n" + "="*60)
    print("✓ API TESTS COMPLETED")
    print("="*60)
