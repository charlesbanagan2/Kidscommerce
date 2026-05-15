"""
Test script to check if juanbuyer@gmail.com can see orders via API
Run this to diagnose the issue
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"  # Change if your backend runs on different port
EMAIL = "juanbuyer@gmail.com"
PASSWORD = "password123"  # Change to actual password

def test_login():
    """Test login and get JWT token"""
    print("=" * 50)
    print("STEP 1: Testing Login")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('access_token')
                user = result.get('user', {})
                print(f"\n✅ Login successful!")
                print(f"User ID: {user.get('id')}")
                print(f"Email: {user.get('email')}")
                print(f"Role: {user.get('role')}")
                print(f"Token: {token[:50]}...")
                return token, user.get('id')
            else:
                print(f"\n❌ Login failed: {result.get('error')}")
                return None, None
        else:
            print(f"\n❌ Login failed with status {response.status_code}")
            return None, None
    except Exception as e:
        print(f"\n❌ Error during login: {e}")
        return None, None

def test_get_orders(token):
    """Test getting orders for the user"""
    print("\n" + "=" * 50)
    print("STEP 2: Testing Get Orders")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/v1/orders/user"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                orders = result.get('orders', [])
                print(f"\n✅ Got {len(orders)} orders")
                
                if len(orders) == 0:
                    print("\n⚠️ NO ORDERS RETURNED!")
                    print("This is the problem - orders exist but API returns empty array")
                else:
                    print("\n✅ Orders found:")
                    for order in orders:
                        print(f"  - Order #{order.get('id')}: {order.get('status')}")
                        
                    # Check if Order #49 is in the list
                    order_49 = next((o for o in orders if o.get('id') == 49), None)
                    if order_49:
                        print(f"\n✅ Order #49 IS in the response!")
                    else:
                        print(f"\n❌ Order #49 is NOT in the response!")
                        print(f"Order IDs returned: {[o.get('id') for o in orders]}")
                
                return orders
            else:
                print(f"\n❌ API returned error: {result.get('error')}")
                return []
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            return []
    except Exception as e:
        print(f"\n❌ Error getting orders: {e}")
        return []

def test_direct_database():
    """Test direct database query"""
    print("\n" + "=" * 50)
    print("STEP 3: Testing Direct Database Query")
    print("=" * 50)
    print("Run this SQL in Supabase SQL Editor:")
    print("-" * 50)
    print(f"""
SELECT 
    o.id,
    o.buyer_id,
    o.status,
    o.total_amount,
    u.email
FROM "order" o
JOIN "user" u ON o.buyer_id = u.id
WHERE u.email = '{EMAIL}'
ORDER BY o.created_at DESC;
    """)
    print("-" * 50)

def main():
    print("\n🔍 DIAGNOSTIC TEST FOR juanbuyer@gmail.com ORDERS")
    print("=" * 50)
    
    # Step 1: Login
    token, user_id = test_login()
    
    if not token:
        print("\n❌ Cannot proceed without valid token")
        print("\nPossible issues:")
        print("1. Backend is not running")
        print("2. Wrong email/password")
        print("3. User account not active")
        return
    
    # Step 2: Get orders
    orders = test_get_orders(token)
    
    # Step 3: Show SQL to run
    test_direct_database()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if len(orders) == 0:
        print("❌ PROBLEM CONFIRMED: API returns 0 orders")
        print("\nPossible causes:")
        print("1. RLS policies blocking the query")
        print("2. Backend filtering incorrectly")
        print("3. No orders exist in database for this user")
        print("\nNext steps:")
        print("1. Run the SQL query above in Supabase")
        print("2. Check if orders exist in database")
        print("3. If orders exist, RLS policies need to be fixed")
    else:
        order_49_found = any(o.get('id') == 49 for o in orders)
        if order_49_found:
            print("✅ Everything working! Order #49 is visible")
        else:
            print("⚠️ Orders returned but Order #49 is missing")
            print(f"Orders found: {[o.get('id') for o in orders]}")
            print("\nPossible causes:")
            print("1. Order #49 doesn't belong to this user")
            print("2. Order #49 doesn't exist")
            print("3. Order #49 has different buyer_id")

if __name__ == "__main__":
    main()
