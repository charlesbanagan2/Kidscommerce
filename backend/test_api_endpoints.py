"""
Test API endpoints for mobile app
"""
import requests
import json

BASE_URL = "http://192.168.1.20:5000"

print("=" * 80)
print("TESTING API ENDPOINTS")
print("=" * 80)

# Test 1: Categories
print("\n1. Testing /api/v1/categories")
try:
    response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Categories count: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"First category: {data[0]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: Products
print("\n2. Testing /api/v1/products")
try:
    response = requests.get(f"{BASE_URL}/api/v1/products?page=1&per_page=20", timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        if isinstance(data, dict):
            if 'products' in data:
                print(f"Products count: {len(data['products'])}")
                if len(data['products']) > 0:
                    print(f"First product: {data['products'][0]}")
            else:
                print(f"Full response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test 3: Products sync
print("\n3. Testing /api/v1/products/sync")
try:
    response = requests.get(f"{BASE_URL}/api/v1/products/sync?last_sync=2024-01-01T00:00:00&per_page=20", timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        if isinstance(data, dict):
            if 'products' in data:
                print(f"Products count: {len(data['products'])}")
            else:
                print(f"Full response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 80)
