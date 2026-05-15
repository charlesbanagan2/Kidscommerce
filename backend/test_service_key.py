import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print("=" * 50)
print("TESTING SUPABASE SERVICE_ROLE KEY")
print("=" * 50)
print(f"URL: {SUPABASE_URL}")
print(f"Service Key: {SERVICE_KEY[:20]}..." if SERVICE_KEY else "Service Key: NOT FOUND")
print()

# Test query: Get orders for buyer_id=25
url = f"{SUPABASE_URL}/rest/v1/order"
headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
}

params = {
    'buyer_id': 'eq.25',
    'select': '*',
    'order': 'created_at.desc'
}

print("Testing query: Get orders for buyer_id=25")
print(f"URL: {url}")
print()

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ SUCCESS! Found {len(orders)} orders")
        print()
        if orders:
            print("First order:")
            print(f"  ID: {orders[0].get('id')}")
            print(f"  Buyer ID: {orders[0].get('buyer_id')}")
            print(f"  Status: {orders[0].get('status')}")
            print(f"  Total: {orders[0].get('total_amount')}")
        else:
            print("⚠️ No orders found for buyer_id=25")
            print("This means:")
            print("  1. Orders exist but buyer_id is different")
            print("  2. Or orders were deleted")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("=" * 50)
