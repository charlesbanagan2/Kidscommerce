"""
Test script for product chat API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test data
TEST_USER_EMAIL = "buyer@gmail.com"  # Change to your test buyer email
TEST_USER_PASSWORD = "Buyer123!"  # Change to your test buyer password
TEST_PRODUCT_ID = 1

def test_login():
    """Test login and get access token"""
    print("\n=== Testing Login ===")
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        tokens = data.get('tokens', {})
        access_token = tokens.get('access_token')
        if access_token:
            print("[OK] Login successful! Token: " + access_token[:20] + "...")
            return access_token
    
    print("[FAIL] Login failed!")
    return None

def test_start_product_chat(access_token, product_id):
    """Test starting a product chat"""
    print(f"\n=== Testing Start Product Chat (Product ID: {product_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/product/start",
        headers=headers,
        json={
            "product_id": product_id,
            "message": "Hi! I'm interested in this product"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("[OK] Product chat started successfully!")
            return True
    
    print("[FAIL] Failed to start product chat!")
    return False

def test_get_product_messages(access_token, product_id):
    """Test getting product chat messages"""
    print(f"\n=== Testing Get Product Messages (Product ID: {product_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/chat/product/{product_id}/messages",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            messages = data.get('messages', [])
            print(f"[OK] Retrieved {len(messages)} messages")
            return True
    
    print("[FAIL] Failed to get messages!")
    return False

def test_send_product_message(access_token, product_id, receiver_id):
    """Test sending a product chat message"""
    print(f"\n=== Testing Send Product Message ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/product/send",
        headers=headers,
        json={
            "product_id": product_id,
            "receiver_id": receiver_id,
            "message": "Is this still available?"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        if data.get('success'):
            print("[OK] Message sent successfully!")
            return True
    
    print("[FAIL] Failed to send message!")
    return False

def main():
    print("=" * 60)
    print("PRODUCT CHAT API TEST")
    print("=" * 60)
    
    # Step 1: Login
    access_token = test_login()
    if not access_token:
        print("\n[ERROR] Cannot proceed without access token")
        return
    
    # Step 2: Start product chat
    success = test_start_product_chat(access_token, TEST_PRODUCT_ID)
    if not success:
        print("\n[WARNING] Start chat failed, but continuing tests...")
    
    # Step 3: Get product messages
    test_get_product_messages(access_token, TEST_PRODUCT_ID)
    
    # Step 4: Send message (assuming seller_id = 2)
    test_send_product_message(access_token, TEST_PRODUCT_ID, receiver_id=2)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
