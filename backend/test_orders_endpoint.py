"""
Test orders endpoint for juanbuyer@gmail.com
"""

import requests
import json

BASE_URL = "http://localhost:5000"
EMAIL = "juanbuyer@gmail.com"
PASSWORD = input("Enter password for juanbuyer@gmail.com: ")

print("\n" + "="*60)
print("TESTING ORDERS ENDPOINT")
print("="*60)

# Step 1: Login
print("\n1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)

print(f"Status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

login_data = login_response.json()
if not login_data.get('success'):
    print(f"❌ Login failed: {login_data.get('error')}")
    exit(1)

token = login_data.get('access_token')
user = login_data.get('user', {})

print(f"✅ Login successful!")
print(f"   User ID: {user.get('id')}")
print(f"   Email: {user.get('email')}")
print(f"   Role: {user.get('role')}")

# Step 2: Get Orders
print("\n2. Getting orders...")
orders_response = requests.get(
    f"{BASE_URL}/api/v1/orders/user",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status: {orders_response.status_code}")
print(f"Response: {json.dumps(orders_response.json(), indent=2)}")

if orders_response.status_code == 200:
    orders_data = orders_response.json()
    if orders_data.get('success'):
        orders = orders_data.get('orders', [])
        print(f"\n✅ Got {len(orders)} orders")
        
        if len(orders) == 0:
            print("\n❌ PROBLEM: API returns 0 orders but database has 8 orders!")
            print("\nPossible causes:")
            print("1. Backend filtering wrong user_id")
            print("2. Backend query has error")
            print("3. Serialization issue")
        else:
            print("\n✅ Orders found:")
            for order in orders:
                print(f"   - Order #{order.get('id')}: {order.get('status')} - ₱{order.get('total_amount')}")
            
            # Check Order #49
            order_49 = next((o for o in orders if o.get('id') == 49), None)
            if order_49:
                print(f"\n✅ Order #49 IS in the response!")
            else:
                print(f"\n❌ Order #49 is NOT in the response!")
                print(f"   Order IDs: {[o.get('id') for o in orders]}")
    else:
        print(f"\n❌ API error: {orders_data.get('error')}")
else:
    print(f"\n❌ Request failed")

print("\n" + "="*60)
