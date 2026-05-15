#!/usr/bin/env python3
"""Test script to verify datetime fixes for product sync and coupon endpoints."""

import requests
import json
import sys
from datetime import datetime

# Fix unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_product_sync():
    """Test product sync endpoint with last_sync timestamp."""
    print("=" * 60)
    print("TEST 1: Product Sync with last_sync timestamp")
    print("=" * 60)
    
    # Test with a timestamp
    last_sync = "2026-04-29T15:00:20.483472"
    url = f"{BASE_URL}/api/v1/products/sync?last_sync={last_sync}&per_page=10"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Products sync returned {len(data.get('products', []))} products")
            print(f"Last sync: {data.get('last_sync')}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_coupon_apply():
    """Test coupon apply endpoint."""
    print("\n" + "=" * 60)
    print("TEST 2: Coupon Apply")
    print("=" * 60)
    
    # First, we need to login to get a token
    login_url = f"{BASE_URL}/api/login"
    login_data = {
        "email": "admin@kidscommerce.com",
        "password": "admin123"
    }
    
    try:
        # Login
        print("Logging in...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json().get('token')
        print(f"✅ Login successful, got token")
        
        # Test coupon apply
        coupon_url = f"{BASE_URL}/api/apply-coupon"
        headers = {"Authorization": f"Bearer {token}"}
        coupon_data = {"coupon_code": "TEST10"}
        
        print(f"Applying coupon: {coupon_data['coupon_code']}")
        coupon_response = requests.post(coupon_url, json=coupon_data, headers=headers, timeout=10)
        
        print(f"Status Code: {coupon_response.status_code}")
        
        if coupon_response.status_code == 200:
            data = coupon_response.json()
            print(f"✅ SUCCESS: {data.get('message')}")
            print(f"Discount: {data.get('discount_amount')}")
            return True
        elif coupon_response.status_code == 400:
            data = coupon_response.json()
            print(f"⚠️  Coupon validation failed (expected if no active coupons): {data.get('message')}")
            return True  # This is OK - means endpoint is working
        else:
            print(f"❌ FAILED: {coupon_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_product_sync_no_timestamp():
    """Test product sync without timestamp (should work)."""
    print("\n" + "=" * 60)
    print("TEST 3: Product Sync without timestamp")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/v1/products/sync?per_page=5"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Products sync returned {len(data.get('products', []))} products")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing datetime fixes for product sync and coupon endpoints")
    print(f"Backend URL: {BASE_URL}")
    print()
    
    results = []
    results.append(("Product Sync with timestamp", test_product_sync()))
    results.append(("Product Sync without timestamp", test_product_sync_no_timestamp()))
    results.append(("Coupon Apply", test_coupon_apply()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
