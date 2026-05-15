import sys
sys.path.insert(0, 'c:/Users/mnban/Documents/kids/backend')
from app import app, db, User, Cart

# Create Flask test client
client = app.test_client()

# Test 1: Login to get token
print("1. Testing login...")
response = client.post('/api/v1/auth/login', json={
    'email': 'carttest123@example.com',
    'password': 'Test@12345'
})
print(f"Login status: {response.status_code}")
data = response.get_json()
token = data.get('tokens', {}).get('access_token')
print(f"Token: {token[:20]}...")

# Test 2: Call the GET /api/v1/buyer/cart endpoint with token
print("\n2. Testing GET /api/v1/buyer/cart...")
headers = {'Authorization': f'Bearer {token}'}
response = client.get('/api/v1/buyer/cart', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_data(as_text=True)[:200]}")

# Test 3: Call POST to add item
print("\n3. Testing POST /api/v1/buyer/cart...")
response = client.post('/api/v1/buyer/cart', 
    json={'product_id': 24, 'quantity': 1},
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_data(as_text=True)[:300]}")
