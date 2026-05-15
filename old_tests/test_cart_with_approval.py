import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("CART ENDPOINT TEST WITH ADMIN APPROVAL")
print("=" * 70)

# Step 1: Register a test buyer
print("\n1. REGISTERING TEST BUYER...")
buyer_email = "cart_test_buyer@example.com"
buyer_password = "Test@1234"

register_response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "email": buyer_email,
    "password": buyer_password,
    "first_name": "Cart",
    "last_name": "Tester",
    "role": "buyer"
})

print(f"   Status: {register_response.status_code}")
reg_data = register_response.json()
print(f"   Response: {json.dumps(reg_data, indent=4)}")

if register_response.status_code != 201 and "already exists" not in register_response.text.lower():
    print("   Registration failed, exiting...")
    exit(1)

# Step 2: Login as admin to approve the user (if admin exists)
print("\n2. LOGGING IN AS ADMIN...")
admin_login = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "admin@example.com",
    "password": "Admin@1234"
})

if admin_login.status_code != 200:
    print(f"   Admin login failed: {admin_login.status_code}")
    # Try alternative admin credentials
    admin_login = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "admin@kids.com",
        "password": "admin123"
    })

if admin_login.status_code == 200:
    admin_data = admin_login.json()
    admin_token = admin_data.get('tokens', {}).get('access_token') or admin_data.get('token')
    print(f"   ✓ Admin logged in!")
    
    # Step 3: Get pending users and approve the newly created one
    print("\n3. FETCHING PENDING USERS TO APPROVE...")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    pending_response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=admin_headers)
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        users = pending_data.get('users', [])
        
        # Find our test buyer in the list
        test_user = None
        for user in users:
            if user.get('email') == buyer_email:
                test_user = user
                break
        
        if test_user:
            user_id = test_user['id']
            print(f"   Found test user: {test_user.get('email')} (ID: {user_id})")
            
            # Approve the user
            print(f"\n4. APPROVING USER...")
            approve_response = requests.post(
                f"{BASE_URL}/api/v1/admin/users/{user_id}/approve",
                headers=admin_headers
            )
            
            if approve_response.status_code in [200, 201]:
                print(f"   ✓ User approved!")
            else:
                print(f"   ✗ Approval failed: {approve_response.status_code}")
                print(f"   Response: {approve_response.json()}")
        else:
            print(f"   ✗ Test user not found in pending list")
    else:
        print(f"   ✗ Could not fetch pending users: {pending_response.status_code}")
else:
    print(f"   Admin login not available, skipping approval")

# Step 4: Now login as the buyer
print("\n5. LOGGING IN AS TEST BUYER...")
buyer_login = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": buyer_email,
    "password": buyer_password
})

if buyer_login.status_code == 200:
    buyer_data = buyer_login.json()
    buyer_token = buyer_data.get('tokens', {}).get('access_token') or buyer_data.get('token')
    print(f"   ✓ Buyer login successful!")
    
    # Step 5: Get products
    print("\n6. FETCHING PRODUCTS...")
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    products_response = requests.get(f"{BASE_URL}/api/v1/products", headers=buyer_headers)
    
    if products_response.status_code == 200:
        products_data = products_response.json()
        products = products_data.get('products', [])
        
        if products:
            product = products[0]
            product_id = product['id']
            product_name = product.get('name', 'Unknown')
            print(f"   ✓ Got product: '{product_name}' (ID: {product_id})")
            
            # Step 6: ADD TO CART
            print("\n7. ADDING PRODUCT TO CART...")
            print(f"   Product ID: {product_id}, Quantity: 1")
            
            cart_response = requests.post(
                f"{BASE_URL}/api/v1/cart",
                json={"product_id": product_id, "quantity": 1},
                headers=buyer_headers
            )
            
            print(f"   Status Code: {cart_response.status_code}")
            cart_data = cart_response.json()
            print(f"   Response: {json.dumps(cart_data, indent=4)}")
            
            if cart_response.status_code in [200, 201]:
                if cart_data.get('success'):
                    print(f"   ✓ SUCCESS! Item added to cart")
                    if cart_data.get('cart_item'):
                        print(f"   Cart item: {cart_data['cart_item']}")
                    else:
                        print(f"   ⚠ Warning: cart_item not in response")
                else:
                    print(f"   ✗ Failed: {cart_data.get('error')}")
            else:
                print(f"   ✗ Error: {cart_response.status_code}")
            
            # Step 7: GET CART to verify
            print("\n8. GETTING CART ITEMS...")
            get_cart_response = requests.get(f"{BASE_URL}/api/v1/cart", headers=buyer_headers)
            
            if get_cart_response.status_code == 200:
                cart_items = get_cart_response.json()
                print(f"   ✓ Cart retrieved: {json.dumps(cart_items, indent=4)}")
            else:
                print(f"   ✗ Error: {get_cart_response.status_code}")
        else:
            print(f"   ✗ No products available")
    else:
        print(f"   ✗ Could not fetch products: {products_response.status_code}")
else:
    print(f"   ✗ Buyer login failed: {buyer_login.status_code}")
    print(f"   Response: {buyer_login.json()}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
