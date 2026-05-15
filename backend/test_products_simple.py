"""
Simple test of products endpoint
"""
import requests
import json

BASE_URL = "http://192.168.1.20:5000"

print("=" * 80)
print("SIMPLE PRODUCTS TEST")
print("=" * 80)

# Test with minimal parameters
print("\nTesting /api/v1/products with minimal params")
try:
    response = requests.get(f"{BASE_URL}/api/v1/products", timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        if isinstance(data, dict) and 'products' in data:
            print(f"Products count: {len(data['products'])}")
            if len(data['products']) > 0:
                print(f"First product keys: {data['products'][0].keys()}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 80)
