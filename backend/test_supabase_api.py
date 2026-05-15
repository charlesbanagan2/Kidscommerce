import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

import requests
import os
from dotenv import load_dotenv

# Load Supabase env
SUPABASE_ENV_PATH = 'c:\\Users\\mnban\\Documents\\kids\\mobile_app\\lib\\kids_commercedb\\supabase.env'
load_dotenv(SUPABASE_ENV_PATH, override=True)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1"

print("=" * 100)
print("TESTING SUPABASE REST API CALLS")
print("=" * 100)

print(f"\nSupabase URL: {SUPABASE_URL}")
print(f"REST URL: {SUPABASE_REST_URL}")
print(f"API Key: {SUPABASE_API_KEY[:20]}...")

headers = {
    'apikey': SUPABASE_API_KEY,
    'Authorization': f'Bearer {SUPABASE_API_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Test 1: Get product by ID
print("\n" + "=" * 100)
print("TEST 1: Get Product 17 by ID")
print("=" * 100)

url1 = f"{SUPABASE_REST_URL}/product?id=eq.17&select=*"
print(f"URL: {url1}")

try:
    response1 = requests.get(url1, headers=headers, timeout=10)
    print(f"Status Code: {response1.status_code}")
    print(f"Response: {response1.text[:500]}")
    
    if response1.status_code == 200:
        data = response1.json()
        if data:
            print(f"\nProduct Found:")
            print(f"  ID: {data[0].get('id')}")
            print(f"  Name: {data[0].get('name')}")
            print(f"  Stock: {data[0].get('stock')}")
            print(f"  Status: {data[0].get('status')}")
        else:
            print("ERROR: Empty response!")
    else:
        print(f"ERROR: {response1.status_code}")
except Exception as e:
    print(f"EXCEPTION: {e}")

# Test 2: Get order_items for product 17
print("\n" + "=" * 100)
print("TEST 2: Get Order Items for Product 17")
print("=" * 100)

url2 = f"{SUPABASE_REST_URL}/order_item?product_id=eq.17&select=*"
print(f"URL: {url2}")

try:
    response2 = requests.get(url2, headers=headers, timeout=10)
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.text[:500]}")
    
    if response2.status_code == 200:
        data = response2.json()
        print(f"Order Items Found: {len(data)}")
    else:
        print(f"ERROR: {response2.status_code}")
except Exception as e:
    print(f"EXCEPTION: {e}")

# Test 3: Get restock_request for product 17
print("\n" + "=" * 100)
print("TEST 3: Get Restock Requests for Product 17")
print("=" * 100)

url3 = f"{SUPABASE_REST_URL}/restock_request?product_id=eq.17&status=eq.pending&select=*"
print(f"URL: {url3}")

try:
    response3 = requests.get(url3, headers=headers, timeout=10)
    print(f"Status Code: {response3.status_code}")
    print(f"Response: {response3.text[:500]}")
    
    if response3.status_code == 200:
        data = response3.json()
        print(f"Restock Requests Found: {len(data)}")
        if data:
            print("WARNING: Pending restock request found - this blocks availability!")
    else:
        print(f"ERROR: {response3.status_code}")
except Exception as e:
    print(f"EXCEPTION: {e}")

# Test 4: List all tables
print("\n" + "=" * 100)
print("TEST 4: Check Available Tables")
print("=" * 100)

# Try common table names
tables_to_test = ['product', 'order', 'order_item', 'restock_request', 'cart', 'user']

for table in tables_to_test:
    url = f"{SUPABASE_REST_URL}/{table}?select=id&limit=1"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"  {table}: EXISTS")
        else:
            print(f"  {table}: ERROR {response.status_code}")
    except Exception as e:
        print(f"  {table}: EXCEPTION {e}")

print("\n" + "=" * 100)
print("DIAGNOSIS")
print("=" * 100)

print("\nIf all tests pass but website shows 0 stock:")
print("1. Check Flask server logs for errors")
print("2. Restart Flask server to clear any caching")
print("3. Check browser console for JavaScript errors")
print("4. Verify get_available_stock() is being called correctly")
