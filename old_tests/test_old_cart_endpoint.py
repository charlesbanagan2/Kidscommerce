import requests
import json

BASE_URL = 'http://192.168.1.20:5000'
headers = {'Content-Type': 'application/json'}

# Test 1: Login
print('1. Testing Login...')
login_response = requests.post(
    f'{BASE_URL}/api/v1/auth/login',
    json={'email': 'carttest123@example.com', 'password': 'Test@12345'},
    headers=headers
)
print(f'Login Status: {login_response.status_code}')

if login_response.status_code == 200:
    response_data = login_response.json()
    token = response_data.get('tokens', {}).get('access_token')
    
    auth_headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 2: Get Cart using OLD /api/v1/buyer/cart endpoint
    print('\n2. Testing OLD GET /api/v1/buyer/cart...')
    cart_get = requests.get(f'{BASE_URL}/api/v1/buyer/cart', headers=auth_headers)
    print(f'GET /api/v1/buyer/cart Status: {cart_get.status_code}')
    print(f'Response: {json.dumps(cart_get.json(), indent=2)[:200]}...')
    
    # Test 3: Add to Cart using OLD /api/v1/buyer/cart endpoint
    print('\n3. Testing OLD POST /api/v1/buyer/cart (Add item)...')
    add_to_cart = requests.post(
        f'{BASE_URL}/api/v1/buyer/cart',
        json={'product_id': 24, 'quantity': 1},
        headers=auth_headers
    )
    print(f'POST /api/v1/buyer/cart Status: {add_to_cart.status_code}')
    response_data = add_to_cart.json()
    print(f'Response: {json.dumps(response_data, indent=2)}')
    
    # Check if cart_item is in response
    if 'cart_item' in response_data:
        print('\n✅ SUCCESS: OLD endpoint returns cart_item!')
    else:
        print('\n❌ ERROR: cart_item NOT in response!')
else:
    print(f'Login failed: {login_response.json()}')
