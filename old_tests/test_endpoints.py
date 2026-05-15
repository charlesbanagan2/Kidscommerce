import requests
import json

BASE_URL = "http://192.168.1.20:5000"

# Test login to get token
print("=" * 60)
print("1️⃣  TESTING LOGIN")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"email": "buyer@test.com", "password": "password123"}
)

if login_response.status_code == 200:
    data = login_response.json()
    access_token = data['tokens']['access_token']
    print("✅ Login successful")
    print(f"Token: {access_token[:50]}...")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit()

headers = {"Authorization": f"Bearer {access_token}"}

# Test cart endpoint
print("\n" + "=" * 60)
print("2️⃣  TESTING /api/v1/buyer/cart")
print("=" * 60)

cart_response = requests.get(f"{BASE_URL}/api/v1/buyer/cart", headers=headers)
print(f"Status: {cart_response.status_code}")
if cart_response.status_code == 200:
    print("✅ Cart endpoint working!")
    print(json.dumps(cart_response.json(), indent=2)[:200] + "...")
else:
    print(f"❌ Cart endpoint failed")
    print(cart_response.text)

# Test orders by status endpoint
print("\n" + "=" * 60)
print("3️⃣  TESTING /api/v1/buyer/orders/by-status")
print("=" * 60)

orders_response = requests.get(
    f"{BASE_URL}/api/v1/buyer/orders/by-status?status=to_pay",
    headers=headers
)
print(f"Status: {orders_response.status_code}")
if orders_response.status_code == 200:
    print("✅ Orders by status endpoint working!")
    data = orders_response.json()
    print(f"   Orders count: {data.get('count', 0)}")
else:
    print(f"❌ Orders endpoint failed")
    print(orders_response.text)

# Test sync endpoint
print("\n" + "=" * 60)
print("4️⃣  TESTING /api/v1/products/sync")
print("=" * 60)

sync_response = requests.get(
    f"{BASE_URL}/api/v1/products/sync?per_page=5"
)
print(f"Status: {sync_response.status_code}")
if sync_response.status_code == 200:
    print("✅ Sync endpoint working!")
    data = sync_response.json()
    print(f"   Products: {data.get('count', 0)}")
    if data.get('products'):
        print(f"   First product: {data['products'][0].get('name')}")
else:
    print(f"❌ Sync endpoint failed")
    print(sync_response.text)

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETE")
print("=" * 60)
