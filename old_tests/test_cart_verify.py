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
    print(f'Response structure: {list(response_data.keys())}')
    
    # Extract token from the correct location
    token = response_data.get('tokens', {}).get('access_token') or response_data.get('access_token')
    
    if not token:
        print('ERROR: No access token in response!')
        print(f'Full response: {response_data}')
        exit(1)
    
    auth_headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 2: Get Cart (should be empty initially)
    print('\n2. Testing GET /api/v1/cart...')
    cart_get = requests.get(f'{BASE_URL}/api/v1/cart', headers=auth_headers)
    print(f'GET Cart Status: {cart_get.status_code}')
    cart_items = cart_get.json()
    print(f'Cart Items Count: {len(cart_items) if isinstance(cart_items, list) else "error"}')
    
    # Test 3: Add to Cart
    print('\n3. Testing POST /api/v1/cart (Add item)...')
    add_to_cart = requests.post(
        f'{BASE_URL}/api/v1/cart',
        json={'product_id': 24, 'quantity': 1},
        headers=auth_headers
    )
    print(f'POST Cart Status: {add_to_cart.status_code}')
    response_data = add_to_cart.json()
    print(f'\nFull Response:')
    print(json.dumps(response_data, indent=2))
    
    # Check if cart_item is in response
    if 'cart_item' in response_data:
        print('\n✅ SUCCESS: cart_item is in response!')
        item = response_data['cart_item']
        print(f'Cart Item Details:')
        print(f'  - ID: {item.get("id")}')
        print(f'  - Product: {item.get("product_name")}')
        print(f'  - Quantity: {item.get("quantity")}')
        print(f'  - Price: {item.get("price")}')
        print(f'  - Subtotal: {item.get("subtotal")}')
    else:
        print('\n❌ ERROR: cart_item NOT in response!')
        print('Response keys:', list(response_data.keys()))
else:
    print(f'Login failed: {login_response.json()}')
