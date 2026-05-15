import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TESTING CART FUNCTIONALITY WITH EXISTING USER")
print("=" * 70)

# Step 1: Login with existing active user
print("\n1. LOGGING IN...")
buyer_email = "test_cart_buyer@example.com"
buyer_password = "Test@1234"

buyer_login = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": buyer_email,
    "password": buyer_password
})

print(f"   Status: {buyer_login.status_code}")
if buyer_login.status_code == 200:
    buyer_data = buyer_login.json()
    print(f"   ✓ Login successful!")
    
    # Get token from response
    token = None
    if 'tokens' in buyer_data and 'access_token' in buyer_data['tokens']:
        token = buyer_data['tokens']['access_token']
    elif 'token' in buyer_data:
        token = buyer_data['token']
    
    if not token:
        print(f"   ✗ No token in response!")
        print(json.dumps(buyer_data, indent=2))
        exit(1)
    
    print(f"   Token: {token[:40]}...")
    
    # Step 2: Get products
    print("\n2. FETCHING PRODUCTS...")
    buyer_headers = {"Authorization": f"Bearer {token}"}
    products_response = requests.get(f"{BASE_URL}/api/v1/products", headers=buyer_headers)
    
    print(f"   Status: {products_response.status_code}")
    if products_response.status_code == 200:
        products_data = products_response.json()
        products = products_data.get('products', [])
        
        if products:
            product = products[0]
            product_id = product['id']
            product_name = product.get('name', 'Unknown')
            product_price = product.get('price', 0)
            print(f"   ✓ Got product: ID={product_id}, Name='{product_name}', Price={product_price}")
            
            # Step 3: ADD TO CART
            print("\n3. ADDING PRODUCT TO CART...")
            print(f"   POST /api/v1/cart")
            print(f"   Body: {{'product_id': {product_id}, 'quantity': 1}}")
            
            cart_response = requests.post(
                f"{BASE_URL}/api/v1/cart",
                json={"product_id": product_id, "quantity": 1},
                headers=buyer_headers
            )
            
            print(f"   Status: {cart_response.status_code}")
            cart_data = cart_response.json()
            print(f"   Response:")
            print(json.dumps(cart_data, indent=4))
            
            if cart_response.status_code in [200, 201]:
                if cart_data.get('success'):
                    print(f"\n   ✓✓✓ SUCCESS! Item added to cart!")
                    if cart_data.get('cart_item'):
                        print(f"       Cart item details:")
                        for key, value in cart_data['cart_item'].items():
                            print(f"         - {key}: {value}")
                    else:
                        print(f"       ⚠ No cart_item in response (client will retry via getCart)")
                else:
                    print(f"\n   ✗ Operation failed: {cart_data.get('error')}")
            else:
                print(f"\n   ✗ HTTP Error: {cart_response.status_code}")
            
            # Step 4: GET CART to verify
            print("\n4. VERIFYING CART CONTENTS...")
            print(f"   GET /api/v1/cart")
            
            get_cart_response = requests.get(f"{BASE_URL}/api/v1/cart", headers=buyer_headers)
            print(f"   Status: {get_cart_response.status_code}")
            
            if get_cart_response.status_code == 200:
                cart_items = get_cart_response.json()
                print(f"   ✓ Cart retrieved:")
                print(json.dumps(cart_items, indent=4))
                
                if cart_items.get('cart_items'):
                    print(f"\n   ✓ Found {len(cart_items['cart_items'])} item(s) in cart")
            else:
                print(f"   ✗ Error: {get_cart_response.status_code}")
                print(f"   Response: {get_cart_response.text}")
        else:
            print(f"   ✗ No products available")
    else:
        print(f"   ✗ Could not fetch products: {products_response.status_code}")
        print(f"   Response: {products_response.text}")
else:
    print(f"   ✗ Login failed: {buyer_login.status_code}")
    print(json.dumps(buyer_login.json(), indent=2))

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
