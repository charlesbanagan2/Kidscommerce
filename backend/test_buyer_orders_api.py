import requests
import json

# Test the buyer orders by-status endpoint
# You need to get the access token for buyer_id 25 first

# Login as buyer 25
login_url = "http://localhost:5000/api/v1/auth/login"
login_data = {
    "email": "juanbuyer@example.com",  # Update with actual email
    "password": "password123"  # Update with actual password
}

print("Logging in as buyer...")
login_response = requests.post(login_url, json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    login_result = login_response.json()
    access_token = login_result.get('access_token')
    
    if access_token:
        print(f"Access token obtained: {access_token[:20]}...")
        
        # Call the orders by-status endpoint
        orders_url = "http://localhost:5000/api/v1/buyer/orders/by-status"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("\nFetching orders by status...")
        orders_response = requests.get(orders_url, headers=headers)
        print(f"Orders API status: {orders_response.status_code}")
        
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            print(f"\nSuccess: {orders_data.get('success')}")
            print(f"\nCounts:")
            print(json.dumps(orders_data.get('counts', {}), indent=2))
            
            print(f"\nTo Pay orders: {len(orders_data.get('to_pay', []))}")
            for order in orders_data.get('to_pay', [])[:5]:  # Show first 5
                print(f"  Order #{order.get('id')}: {order.get('status')} - PHP {order.get('total_amount')}")
            
            print(f"\nAll orders (first 5):")
            all_statuses = ['to_pay', 'to_ship', 'to_receive', 'completed', 'returns', 'cancelled']
            for status in all_statuses:
                orders = orders_data.get(status, [])
                if orders:
                    print(f"\n{status.upper()}: {len(orders)} orders")
                    for order in orders[:3]:
                        print(f"  Order #{order.get('id')}: {order.get('status')}")
        else:
            print(f"Error: {orders_response.text}")
    else:
        print("No access token in response")
else:
    print(f"Login failed: {login_response.text}")
