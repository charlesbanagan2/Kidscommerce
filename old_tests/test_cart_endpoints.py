import requests
import json

# Test cart functionality
BASE_URL = "http://localhost:5000"

print("=" * 60)
print("TESTING CART FUNCTIONALITY")
print("=" * 60)

# First, login to get a token
print("\n1. Testing LOGIN...")
login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "charliebanagan33@gmail.com",
    "password": "password123"
})

if login_response.status_code == 200:
    login_data = login_response.json()
    if login_data.get('success') and login_data.get('token'):
        token = login_data['token']
        print(f"✓ Login successful! Token: {token[:20]}...")
        
        # Now test adding to cart
        print("\n2. Testing ADD TO CART...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get products first to know what to add
        products_response = requests.get(f"{BASE_URL}/api/v1/products", headers=headers)
        if products_response.status_code == 200:
            products_data = products_response.json()
            if products_data.get('products') and len(products_data['products']) > 0:
                product = products_data['products'][0]
                product_id = product.get('id')
                print(f"  Found product: {product.get('name')} (ID: {product_id})")
                
                # Add to cart
                cart_response = requests.post(
                    f"{BASE_URL}/api/v1/cart",
                    json={"product_id": product_id, "quantity": 1},
                    headers=headers
                )
                
                print(f"  Response Status: {cart_response.status_code}")
                print(f"  Response Body: {json.dumps(cart_response.json(), indent=2)}")
                
                if cart_response.status_code in [200, 201]:
                    cart_data = cart_response.json()
                    if cart_data.get('success'):
                        if cart_data.get('cart_item'):
                            print(f"  ✓ Cart item returned: {cart_data['cart_item']}")
                        else:
                            print(f"  ⚠ No cart_item in response - checking if it needs fallback fetch...")
                    else:
                        print(f"  ✗ Failed: {cart_data.get('error')}")
                else:
                    print(f"  ✗ Error: {cart_response.text}")
            else:
                print(f"  ✗ No products found")
        else:
            print(f"  ✗ Could not fetch products: {products_response.status_code}")
        
        # Get cart items
        print("\n3. Testing GET CART...")
        cart_get_response = requests.get(f"{BASE_URL}/api/v1/cart", headers=headers)
        print(f"  Response Status: {cart_get_response.status_code}")
        if cart_get_response.status_code == 200:
            cart_items = cart_get_response.json()
            print(f"  ✓ Cart items: {json.dumps(cart_items, indent=2)}")
        else:
            print(f"  ✗ Error: {cart_get_response.text}")
    else:
        print(f"✗ Login failed: {login_response.json()}")
else:
    print(f"✗ Login error: {login_response.status_code}")

print("\n" + "=" * 60)
print("CART TEST COMPLETE")
print("=" * 60)
