import requests
import json

BASE_URL = "http://localhost:5000"

# First, check if we need to register
print("Attempting to register test user...")
register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "email": "testbuyer@example.com",
    "password": "Test@1234",
    "role": "buyer"
})

print(f"Register response: {register_response.status_code}")
print(json.dumps(register_response.json(), indent=2))

if register_response.status_code == 201 or (register_response.status_code == 400 and "already exists" in register_response.text.lower()):
    print("\nNow trying to login...")
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "testbuyer@example.com",
        "password": "Test@1234"
    })
    
    print(f"Login response: {login_response.status_code}")
    login_data = login_response.json()
    print(json.dumps(login_data, indent=2))
    
    if login_response.status_code == 200 and login_data.get('token'):
        token = login_data['token']
        print(f"\n✓ Successfully logged in! Token: {token[:30]}...")
        
        # Test adding a product to cart
        print("\n" + "="*60)
        print("Testing ADD TO CART")
        print("="*60)
        
        # First get a product
        headers = {"Authorization": f"Bearer {token}"}
        products_response = requests.get(f"{BASE_URL}/api/v1/products", headers=headers)
        
        if products_response.status_code == 200:
            products_data = products_response.json()
            products = products_data.get('products', [])
            
            if products:
                product = products[0]
                product_id = product['id']
                print(f"Adding product '{product['name']}' (ID: {product_id}) to cart...")
                
                # Add to cart
                add_response = requests.post(
                    f"{BASE_URL}/api/v1/cart",
                    json={"product_id": product_id, "quantity": 1},
                    headers=headers
                )
                
                print(f"Add to cart response: {add_response.status_code}")
                add_data = add_response.json()
                print(json.dumps(add_data, indent=2))
                
                if add_response.status_code in [200, 201] and add_data.get('success'):
                    print("\n✓ ITEM ADDED SUCCESSFULLY!")
                    if add_data.get('cart_item'):
                        print(f"Cart item data: {add_data['cart_item']}")
                    else:
                        print("⚠ Warning: cart_item not in response")
                else:
                    print(f"\n✗ Failed to add item: {add_data.get('error')}")
            else:
                print("No products available")
        else:
            print(f"Could not fetch products: {products_response.status_code}")
    else:
        print(f"Login failed: {login_data}")
