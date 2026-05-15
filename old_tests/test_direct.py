import sys
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')

from app import app

# Create a test client
client = app.test_client()

# First login to get a token
print("Logging in to get token...")
login_response = client.post('/api/v1/auth/login', 
    json={"email": "buyer@test.com", "password": "password123"},
    content_type='application/json'
)
data = login_response.get_json()
token = data['tokens']['access_token']
print(f"Token: {token[:50]}...")

headers = {"Authorization": f"Bearer {token}"}

# Now test the cart endpoint WITH token
print("\nTesting /api/v1/buyer/cart WITH TOKEN:")
response = client.get('/api/v1/buyer/cart', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

print("\nTesting /api/v1/buyer/orders/by-status WITH TOKEN:")
response = client.get('/api/v1/buyer/orders/by-status?status=to_pay', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")
