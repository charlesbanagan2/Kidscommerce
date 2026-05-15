import requests
import json

# Configuration
BASE_URL = "http://192.168.1.20:5000"
TEST_EMAIL = "test@gmail.com"
TEST_PASSWORD = "test123"

def test_checkout():
    print("=" * 60)
    print("CHECKOUT ENDPOINT TEST")
    print("=" * 60)
    
    # Step 1: Login to get tokens
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    if 'tokens' not in login_data:
        print(f"❌ No tokens in response: {login_data}")
        return False
    
    access_token = login_data['tokens']['access_token']
    print(f"✅ Login successful")
    print(f"   Token: {access_token[:30]}...")
    
    # Step 2: Get cart items
    print("\n2. Fetching cart...")
    cart_response = requests.get(
        f"{BASE_URL}/api/v1/buyer/cart",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    if cart_response.status_code != 200:
        print(f"❌ Cart fetch failed: {cart_response.status_code}")
        print(f"Response: {cart_response.text}")
        return False
    
    cart_items = cart_response.json()
    if not cart_items or len(cart_items) == 0:
        print("⚠️  Cart is empty, adding a test item...")
        
        # Get first available product
        products_response = requests.get(f"{BASE_URL}/api/v1/products?page=1&per_page=1")
        if products_response.status_code == 200:
            products_data = products_response.json()
            if 'products' in products_data and len(products_data['products']) > 0:
                product_id = products_data['products'][0]['id']
                
                # Add to cart
                add_response = requests.post(
                    f"{BASE_URL}/api/v1/buyer/cart",
                    json={"product_id": product_id, "quantity": 1},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if add_response.status_code == 200:
                    print(f"✅ Added product {product_id} to cart")
                    # Fetch cart again
                    cart_response = requests.get(
                        f"{BASE_URL}/api/v1/buyer/cart",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json"
                        }
                    )
                    cart_items = cart_response.json()
                else:
                    print(f"❌ Failed to add to cart: {add_response.text}")
                    return False
    
    print(f"✅ Cart has {len(cart_items)} item(s)")
    
    # Get cart item IDs
    selected_items = [item['id'] for item in cart_items]
    print(f"   Selected items: {selected_items}")
    
    # Step 3: Test checkout
    print("\n3. Testing checkout...")
    checkout_data = {
        "recipient_name": "Test User",
        "recipient_phone": "09123456789",
        "shipping_address": "Test Address, Test City, Test Province",
        "payment_method": "cod",
        "notes": "Test order from automated test",
        "selected_items": selected_items,
        "shipping_fee": 10.0
    }
    
    print(f"   Request body: {json.dumps(checkout_data, indent=2)}")
    
    checkout_response = requests.post(
        f"{BASE_URL}/api/v1/buyer/checkout",
        json=checkout_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"\n4. Response Status: {checkout_response.status_code}")
    
    if checkout_response.status_code != 200:
        print(f"❌ Checkout failed!")
        print(f"Response: {checkout_response.text}")
        return False
    
    response_data = checkout_response.json()
    print(f"\n5. Response Data:")
    print(json.dumps(response_data, indent=2))
    
    # Validate response structure
    print("\n6. Validating response structure...")
    
    if 'success' not in response_data:
        print("❌ Missing 'success' field")
        return False
    
    if response_data['success'] != True:
        print(f"❌ Success is False: {response_data.get('error', 'Unknown error')}")
        return False
    
    if 'order' not in response_data:
        print("❌ Missing 'order' field")
        return False
    
    order = response_data['order']
    
    required_fields = ['id', 'buyer_id', 'total_amount', 'status', 'payment_method', 
                      'shipping_address', 'recipient_name', 'recipient_phone', 'items']
    
    missing_fields = [field for field in required_fields if field not in order]
    
    if missing_fields:
        print(f"❌ Missing required fields in order: {missing_fields}")
        return False
    
    if not isinstance(order['items'], list):
        print("❌ 'items' is not a list")
        return False
    
    if len(order['items']) == 0:
        print("❌ Order has no items")
        return False
    
    print("✅ All required fields present")
    print(f"   Order ID: {order['id']}")
    print(f"   Status: {order['status']}")
    print(f"   Total: ₱{order['total_amount']}")
    print(f"   Items: {len(order['items'])}")
    
    for idx, item in enumerate(order['items'], 1):
        print(f"   Item {idx}: {item.get('product_name', 'Unknown')} x{item.get('quantity', 0)} @ ₱{item.get('price', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ CHECKOUT TEST PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_checkout()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
