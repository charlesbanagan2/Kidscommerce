"""
Detailed test of API endpoints
"""
import requests
import json

BASE_URL = "http://192.168.1.20:5000"

print("=" * 80)
print("DETAILED API TESTING")
print("=" * 80)

# Test 1: Categories
print("\n1. Testing /api/v1/categories")
try:
    response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:1000]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 80)
