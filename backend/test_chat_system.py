"""
COMPREHENSIVE CHAT SYSTEM TEST
Tests all chat functionality for Buyer, Seller, and Rider roles
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_V1 = f"{BASE_URL}/api/v1"

# Test credentials (update these with actual test accounts)
TEST_USERS = {
    'buyer': {
        'email': 'buyer@gmail.com',
        'password': 'Buyer123!',
        'token': None,
        'user_id': None
    },
    'seller': {
        'email': 'seller@gmail.com',
        'password': 'Seller123!',
        'token': None,
        'user_id': None
    },
    'rider': {
        'email': 'rider@gmail.com',
        'password': 'Rider123!',
        'token': None,
        'user_id': None
    }
}

# Test product ID (update with actual product ID)
TEST_PRODUCT_ID = 1

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.RESET}\n")

# ============================================
# AUTHENTICATION
# ============================================

def login_user(role):
    """Login and get JWT token"""
    print_info(f"Logging in as {role}...")
    
    response = requests.post(
        f"{API_V1}/auth/login",
        json={
            'email': TEST_USERS[role]['email'],
            'password': TEST_USERS[role]['password']
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        TEST_USERS[role]['token'] = data.get('access_token')
        TEST_USERS[role]['user_id'] = data.get('user', {}).get('id')
        print_success(f"{role.capitalize()} logged in successfully")
        print_info(f"User ID: {TEST_USERS[role]['user_id']}")
        return True
    else:
        print_error(f"Failed to login as {role}: {response.text}")
        return False

def get_headers(role):
    """Get authorization headers for API calls"""
    return {
        'Authorization': f"Bearer {TEST_USERS[role]['token']}",
        'Content-Type': 'application/json'
    }

# ============================================
# CHAT TESTS
# ============================================

def test_get_conversations(role):
    """Test getting all conversations"""
    print_info(f"Testing get conversations for {role}...")
    
    response = requests.get(
        f"{API_V1}/chat/conversations",
        headers=get_headers(role)
    )
    
    if response.status_code == 200:
        data = response.json()
        conversations = data.get('conversations', [])
        print_success(f"Got {len(conversations)} conversations")
        
        for conv in conversations[:3]:  # Show first 3
            print(f"  - {conv['peer_name']} ({conv['peer_role']}): {conv['last_message'][:50]}...")
        
        return True
    else:
        print_error(f"Failed to get conversations: {response.text}")
        return False

def test_send_message(sender_role, receiver_role, message):
    """Test sending a direct message"""
    print_info(f"Testing {sender_role} → {receiver_role} message...")
    
    receiver_id = TEST_USERS[receiver_role]['user_id']
    
    response = requests.post(
        f"{API_V1}/chat/send",
        headers=get_headers(sender_role),
        json={
            'receiver_id': receiver_id,
            'message': message
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        msg = data.get('message', {})
        print_success(f"Message sent successfully (ID: {msg.get('id')})")
        print(f"  Message: {msg.get('message')}")
        return msg.get('id')
    else:
        print_error(f"Failed to send message: {response.text}")
        return None

def test_get_messages(role, other_role):
    """Test getting messages with another user"""
    print_info(f"Testing get messages between {role} and {other_role}...")
    
    other_user_id = TEST_USERS[other_role]['user_id']
    
    response = requests.get(
        f"{API_V1}/chat/messages/{other_user_id}",
        headers=get_headers(role)
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        print_success(f"Got {len(messages)} messages")
        
        for msg in messages[-3:]:  # Show last 3
            sender_name = msg['sender']['name']
            print(f"  - {sender_name}: {msg['message'][:50]}...")
        
        return True
    else:
        print_error(f"Failed to get messages: {response.text}")
        return False

def test_unread_count(role):
    """Test getting unread message count"""
    print_info(f"Testing unread count for {role}...")
    
    response = requests.get(
        f"{API_V1}/chat/unread-count",
        headers=get_headers(role)
    )
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('unread_count', 0)
        print_success(f"Unread messages: {count}")
        return True
    else:
        print_error(f"Failed to get unread count: {response.text}")
        return False

# ============================================
# PRODUCT CHAT TESTS
# ============================================

def test_start_product_chat(buyer_role='buyer'):
    """Test starting a product chat"""
    print_info(f"Testing start product chat...")
    
    response = requests.post(
        f"{API_V1}/chat/product/start",
        headers=get_headers(buyer_role),
        json={
            'product_id': TEST_PRODUCT_ID,
            'message': f"Hi! I'm interested in this product. Is it still available? (Test at {datetime.now().strftime('%H:%M:%S')})"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        conv = data.get('conversation', {})
        print_success(f"Product chat started with seller ID: {conv.get('peer_id')}")
        return True
    else:
        print_error(f"Failed to start product chat: {response.text}")
        return False

def test_send_product_message(role, message):
    """Test sending a product-related message"""
    print_info(f"Testing send product message from {role}...")
    
    response = requests.post(
        f"{API_V1}/chat/product/send",
        headers=get_headers(role),
        json={
            'product_id': TEST_PRODUCT_ID,
            'message': message
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        msg = data.get('message', {})
        print_success(f"Product message sent (ID: {msg.get('id')})")
        print(f"  Message: {msg.get('message')}")
        return True
    else:
        print_error(f"Failed to send product message: {response.text}")
        return False

def test_get_product_messages(role):
    """Test getting product chat messages"""
    print_info(f"Testing get product messages for {role}...")
    
    response = requests.get(
        f"{API_V1}/chat/product/{TEST_PRODUCT_ID}/messages",
        headers=get_headers(role)
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        product = data.get('product', {})
        print_success(f"Got {len(messages)} messages for product: {product.get('name')}")
        
        for msg in messages[-3:]:  # Show last 3
            sender_name = msg['sender']['name']
            print(f"  - {sender_name}: {msg['message'][:50]}...")
        
        return True
    else:
        print_error(f"Failed to get product messages: {response.text}")
        return False

def test_get_product_conversations(role):
    """Test getting all product conversations"""
    print_info(f"Testing get product conversations for {role}...")
    
    response = requests.get(
        f"{API_V1}/chat/conversations/product",
        headers=get_headers(role)
    )
    
    if response.status_code == 200:
        data = response.json()
        conversations = data.get('conversations', [])
        print_success(f"Got {len(conversations)} product conversations")
        
        for conv in conversations[:3]:  # Show first 3
            print(f"  - {conv['product_name']}: {conv['last_message'][:50]}...")
        
        return True
    else:
        print_error(f"Failed to get product conversations: {response.text}")
        return False

# ============================================
# MAIN TEST SUITE
# ============================================

def run_all_tests():
    """Run all chat tests"""
    print_section("CHAT SYSTEM COMPREHENSIVE TEST")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    def record_result(success):
        results['total'] += 1
        if success:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # ============================================
    # STEP 1: LOGIN ALL USERS
    # ============================================
    print_section("STEP 1: Authentication")
    
    for role in ['buyer', 'seller', 'rider']:
        if not login_user(role):
            print_error(f"Cannot proceed without {role} login")
            return
    
    time.sleep(1)
    
    # ============================================
    # STEP 2: BUYER → SELLER PRODUCT CHAT
    # ============================================
    print_section("STEP 2: Buyer → Seller Product Chat")
    
    record_result(test_start_product_chat('buyer'))
    time.sleep(0.5)
    
    record_result(test_send_product_message('buyer', 
        f"What's the shipping cost to Manila? (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_product_messages('buyer'))
    time.sleep(0.5)
    
    record_result(test_get_product_conversations('buyer'))
    time.sleep(1)
    
    # ============================================
    # STEP 3: SELLER RESPONDS TO BUYER
    # ============================================
    print_section("STEP 3: Seller → Buyer Response")
    
    record_result(test_get_product_messages('seller'))
    time.sleep(0.5)
    
    record_result(test_send_product_message('seller', 
        f"Shipping to Manila is ₱50. Product is available! (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_product_conversations('seller'))
    time.sleep(1)
    
    # ============================================
    # STEP 4: DIRECT MESSAGING (BUYER ↔ SELLER)
    # ============================================
    print_section("STEP 4: Direct Messaging (Buyer ↔ Seller)")
    
    record_result(test_send_message('buyer', 'seller', 
        f"Can I get a discount for bulk orders? (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('buyer', 'seller'))
    time.sleep(0.5)
    
    record_result(test_send_message('seller', 'buyer', 
        f"Yes! 10% off for orders of 5+ items. (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('seller', 'buyer'))
    time.sleep(1)
    
    # ============================================
    # STEP 5: BUYER ↔ RIDER CHAT
    # ============================================
    print_section("STEP 5: Direct Messaging (Buyer ↔ Rider)")
    
    record_result(test_send_message('buyer', 'rider', 
        f"Hi! Can you deliver to Quezon City? (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('buyer', 'rider'))
    time.sleep(0.5)
    
    record_result(test_send_message('rider', 'buyer', 
        f"Yes, I can deliver there. ETA 30 minutes. (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('rider', 'buyer'))
    time.sleep(1)
    
    # ============================================
    # STEP 6: SELLER ↔ RIDER CHAT
    # ============================================
    print_section("STEP 6: Direct Messaging (Seller ↔ Rider)")
    
    record_result(test_send_message('seller', 'rider', 
        f"Order #123 is ready for pickup. (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('seller', 'rider'))
    time.sleep(0.5)
    
    record_result(test_send_message('rider', 'seller', 
        f"On my way to pick it up! (Test at {datetime.now().strftime('%H:%M:%S')})"))
    time.sleep(0.5)
    
    record_result(test_get_messages('rider', 'seller'))
    time.sleep(1)
    
    # ============================================
    # STEP 7: CHECK CONVERSATIONS & UNREAD
    # ============================================
    print_section("STEP 7: Conversations & Unread Counts")
    
    for role in ['buyer', 'seller', 'rider']:
        record_result(test_get_conversations(role))
        time.sleep(0.3)
        record_result(test_unread_count(role))
        time.sleep(0.3)
    
    # ============================================
    # FINAL RESULTS
    # ============================================
    print_section("TEST RESULTS SUMMARY")
    
    print(f"Total Tests: {results['total']}")
    print_success(f"Passed: {results['passed']}")
    
    if results['failed'] > 0:
        print_error(f"Failed: {results['failed']}")
    else:
        print_success("All tests passed! ✓")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print_success("\n🎉 CHAT SYSTEM IS FULLY FUNCTIONAL! 🎉")
    elif success_rate >= 80:
        print_warning("\n⚠️  Chat system mostly working, some issues detected")
    else:
        print_error("\n❌ Chat system has significant issues")

# ============================================
# QUICK TESTS
# ============================================

def quick_test_buyer_seller():
    """Quick test for buyer-seller chat only"""
    print_section("QUICK TEST: Buyer ↔ Seller Chat")
    
    if not login_user('buyer') or not login_user('seller'):
        return
    
    test_start_product_chat('buyer')
    time.sleep(0.5)
    test_send_product_message('buyer', "Quick test message from buyer")
    time.sleep(0.5)
    test_get_product_messages('seller')
    time.sleep(0.5)
    test_send_product_message('seller', "Quick test response from seller")
    time.sleep(0.5)
    test_get_product_messages('buyer')
    
    print_success("\nQuick test completed!")

def quick_test_all_roles():
    """Quick test for all role combinations"""
    print_section("QUICK TEST: All Role Combinations")
    
    for role in ['buyer', 'seller', 'rider']:
        if not login_user(role):
            return
    
    # Test each combination
    test_send_message('buyer', 'seller', "Buyer → Seller test")
    time.sleep(0.3)
    test_send_message('buyer', 'rider', "Buyer → Rider test")
    time.sleep(0.3)
    test_send_message('seller', 'rider', "Seller → Rider test")
    time.sleep(0.3)
    
    # Check conversations
    for role in ['buyer', 'seller', 'rider']:
        test_get_conversations(role)
        time.sleep(0.3)
    
    print_success("\nQuick test completed!")

# ============================================
# RUN TESTS
# ============================================

if __name__ == "__main__":
    import sys
    
    print(f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          CHAT SYSTEM COMPREHENSIVE TEST SUITE             ║
║                                                            ║
║  Tests: Buyer ↔ Seller ↔ Rider messaging                 ║
║         Product chat, Direct chat, Conversations          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.RESET}
    """)
    
    print_warning("IMPORTANT: Update TEST_USERS credentials and TEST_PRODUCT_ID before running!")
    print_info("Make sure the backend server is running on http://localhost:5000\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'quick':
            quick_test_all_roles()
        elif sys.argv[1] == 'buyer-seller':
            quick_test_buyer_seller()
        else:
            print_error(f"Unknown test mode: {sys.argv[1]}")
            print_info("Usage: python test_chat_system.py [quick|buyer-seller]")
    else:
        run_all_tests()
