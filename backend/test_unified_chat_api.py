"""
Unified Chat API Test Suite
Tests all buyer-seller and buyer-rider chat functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Test users - UPDATED WITH REAL TOKENS
TEST_USERS = {
    'buyer': {
        'id': 10,
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwicm9sZSI6ImJ1eWVyIiwiZXhwIjoxNzgxOTM5NDU5fQ.iYEhbyhwC5Ntz20NDv0VlhHGWisWnIU73ErhlI-sLl0',
        'role': 'buyer'
    },
    'seller': {
        'id': 11,
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwicm9sZSI6InNlbGxlciIsImV4cCI6MTc4MTkzOTQ1OX0.PYiLTC5TeC_2bI_ofAGMfopMUerJR8W9DZ9eup-PO3g',
        'role': 'seller'
    },
    'rider': {
        'id': 12,
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMiwicm9sZSI6InJpZGVyIiwiZXhwIjoxNzgxOTM5NDU5fQ._TaIwH7bctp4uKdwlNmikjzj4-e7T7pV1ycHpptJiMY',
        'role': 'rider'
    }
}

# Test data
TEST_PRODUCT_ID = 2  # Disney Mickey Mouse Choose Happy Set
TEST_ORDER_ID = 50   # Completed order

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def print_test(test_name):
    """Print test name"""
    print(f"{Colors.BLUE}🧪 Testing: {test_name}{Colors.RESET}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

def get_headers(user_type):
    """Get authorization headers for a user type"""
    token = TEST_USERS[user_type]['token']
    if not token:
        raise ValueError(f"No token set for {user_type}. Please update TEST_USERS in the script.")
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def test_send_message(sender_type, receiver_type, message_text, product_id=None, order_id=None):
    """Test sending a message"""
    test_name = f"{sender_type.capitalize()} → {receiver_type.capitalize()}"
    if product_id:
        test_name += f" (product_id={product_id})"
    if order_id:
        test_name += f" (order_id={order_id})"
    
    print_test(test_name)
    
    try:
        receiver_id = TEST_USERS[receiver_type]['id']
        if not receiver_id:
            print_error(f"Receiver ID not set for {receiver_type}")
            return None
        
        payload = {
            'receiver_id': receiver_id,
            'message': message_text
        }
        
        if product_id:
            payload['product_id'] = product_id
        if order_id:
            payload['order_id'] = order_id
        
        response = requests.post(
            f"{API_BASE}/chat/send",
            headers=get_headers(sender_type),
            json=payload
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                msg_id = data['message']['id']
                print_success(f"Message sent successfully (ID: {msg_id})")
                print_info(f"Response: {json.dumps(data, indent=2)}")
                return data['message']
            else:
                print_error(f"API returned success=false: {data}")
                return None
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_get_messages(user_type, other_user_type):
    """Test getting messages with another user"""
    test_name = f"Get messages: {user_type.capitalize()} ↔ {other_user_type.capitalize()}"
    print_test(test_name)
    
    try:
        other_user_id = TEST_USERS[other_user_type]['id']
        if not other_user_id:
            print_error(f"Other user ID not set for {other_user_type}")
            return None
        
        response = requests.get(
            f"{API_BASE}/chat/messages/{other_user_id}",
            headers=get_headers(user_type)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                messages = data['messages']
                print_success(f"Retrieved {len(messages)} messages")
                
                # Verify ordering (ascending by created_at)
                if len(messages) > 1:
                    timestamps = [msg['created_at'] for msg in messages]
                    is_sorted = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
                    if is_sorted:
                        print_success("Messages are correctly ordered by created_at (ascending)")
                    else:
                        print_error("Messages are NOT correctly ordered")
                
                # Show last 3 messages
                if messages:
                    print_info("Last 3 messages:")
                    for msg in messages[-3:]:
                        sender_name = msg['sender']['name']
                        text = msg['message'][:50]
                        print(f"  - {sender_name}: {text}")
                
                return messages
            else:
                print_error(f"API returned success=false: {data}")
                return None
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_mark_read(user_type, other_user_type):
    """Test marking messages as read"""
    test_name = f"Mark as read: {user_type.capitalize()} marks messages from {other_user_type.capitalize()}"
    print_test(test_name)
    
    try:
        other_user_id = TEST_USERS[other_user_type]['id']
        if not other_user_id:
            print_error(f"Other user ID not set for {other_user_type}")
            return False
        
        response = requests.post(
            f"{API_BASE}/chat/mark-read/{other_user_id}",
            headers=get_headers(user_type)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                marked_count = data.get('marked_count', 0)
                print_success(f"Marked {marked_count} messages as read")
                return True
            else:
                print_error(f"API returned success=false: {data}")
                return False
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_unread_count(user_type):
    """Test getting unread message count"""
    test_name = f"Get unread count for {user_type.capitalize()}"
    print_test(test_name)
    
    try:
        response = requests.get(
            f"{API_BASE}/chat/unread-count",
            headers=get_headers(user_type)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = data.get('unread_count', 0)
                print_success(f"Unread count: {count}")
                return count
            else:
                print_error(f"API returned success=false: {data}")
                return None
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_conversations(user_type):
    """Test getting conversation list"""
    test_name = f"Get conversations for {user_type.capitalize()}"
    print_test(test_name)
    
    try:
        response = requests.get(
            f"{API_BASE}/chat/conversations",
            headers=get_headers(user_type)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                conversations = data['conversations']
                print_success(f"Retrieved {len(conversations)} conversations")
                
                # Verify each conversation has required fields
                required_fields = ['peer_id', 'peer_name', 'peer_role', 'last_message', 'last_message_time', 'unread_count']
                for conv in conversations:
                    missing = [f for f in required_fields if f not in conv]
                    if missing:
                        print_error(f"Conversation missing fields: {missing}")
                    else:
                        print_info(f"  - {conv['peer_name']} ({conv['peer_role']}): {conv['last_message'][:30] if conv['last_message'] else 'No messages'} | Unread: {conv['unread_count']}")
                
                return conversations
            else:
                print_error(f"API returned success=false: {data}")
                return None
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_product_chat():
    """Test product chat functionality"""
    print_header("TASK 7.1: BUYER-SELLER CHAT (PRODUCT CONTEXT)")
    
    # Test 1: Buyer sends message to seller with product_id
    msg1 = test_send_message(
        'buyer', 'seller',
        f"Hi! I'm interested in this product. Is it still available? (Test at {datetime.now().strftime('%H:%M:%S')})",
        product_id=TEST_PRODUCT_ID
    )
    time.sleep(1)
    
    # Test 2: Seller replies to buyer with product_id
    msg2 = test_send_message(
        'seller', 'buyer',
        f"Yes, it's available! Would you like to purchase it? (Test at {datetime.now().strftime('%H:%M:%S')})",
        product_id=TEST_PRODUCT_ID
    )
    time.sleep(1)
    
    # Test 3: Get messages (buyer perspective)
    messages_buyer = test_get_messages('buyer', 'seller')
    time.sleep(1)
    
    # Test 4: Get messages (seller perspective)
    messages_seller = test_get_messages('seller', 'buyer')
    time.sleep(1)
    
    # Test 5: Check unread count (buyer)
    unread_buyer_before = test_unread_count('buyer')
    time.sleep(1)
    
    # Test 6: Mark messages as read (buyer)
    test_mark_read('buyer', 'seller')
    time.sleep(1)
    
    # Test 7: Check unread count after marking as read (buyer)
    unread_buyer_after = test_unread_count('buyer')
    time.sleep(1)
    
    # Test 8: Get conversations (buyer)
    conversations_buyer = test_conversations('buyer')
    time.sleep(1)
    
    # Test 9: Get conversations (seller)
    conversations_seller = test_conversations('seller')
    
    # Summary
    print_header("TASK 7.1 SUMMARY")
    tests_passed = 0
    tests_total = 9
    
    if msg1: tests_passed += 1
    if msg2: tests_passed += 1
    if messages_buyer: tests_passed += 1
    if messages_seller: tests_passed += 1
    if unread_buyer_before is not None: tests_passed += 1
    if unread_buyer_after is not None: tests_passed += 1
    if conversations_buyer: tests_passed += 1
    if conversations_seller: tests_passed += 1
    
    # Check if unread count decreased after marking as read
    if unread_buyer_before is not None and unread_buyer_after is not None:
        if unread_buyer_after <= unread_buyer_before:
            print_success("Unread count correctly decreased after marking as read")
            tests_passed += 1
        else:
            print_error("Unread count did NOT decrease after marking as read")
    
    print(f"\n{Colors.BOLD}Tests Passed: {tests_passed}/{tests_total}{Colors.RESET}")
    
    if tests_passed == tests_total:
        print_success("✅ ALL TESTS PASSED!")
    else:
        print_warning(f"⚠️  {tests_total - tests_passed} tests failed")

def test_order_chat():
    """Test order chat functionality (buyer-rider)"""
    print_header("TASK 7.2: BUYER-RIDER CHAT (ORDER CONTEXT)")
    
    # Test 1: Buyer sends message to rider with order_id
    msg1 = test_send_message(
        'buyer', 'rider',
        f"Hi! Can you deliver to my address? (Test at {datetime.now().strftime('%H:%M:%S')})",
        order_id=TEST_ORDER_ID
    )
    time.sleep(1)
    
    # Test 2: Rider replies to buyer with order_id
    msg2 = test_send_message(
        'rider', 'buyer',
        f"Yes, I'm on my way! ETA 15 minutes. (Test at {datetime.now().strftime('%H:%M:%S')})",
        order_id=TEST_ORDER_ID
    )
    time.sleep(1)
    
    # Test 3: Get messages (buyer perspective)
    messages_buyer = test_get_messages('buyer', 'rider')
    time.sleep(1)
    
    # Test 4: Get messages (rider perspective)
    messages_rider = test_get_messages('rider', 'buyer')
    time.sleep(1)
    
    # Test 5: Check unread count (buyer)
    unread_buyer = test_unread_count('buyer')
    time.sleep(1)
    
    # Test 6: Check unread count (rider)
    unread_rider = test_unread_count('rider')
    time.sleep(1)
    
    # Test 7: Get conversations (buyer)
    conversations_buyer = test_conversations('buyer')
    time.sleep(1)
    
    # Test 8: Get conversations (rider)
    conversations_rider = test_conversations('rider')
    
    # Summary
    print_header("TASK 7.2 SUMMARY")
    tests_passed = 0
    tests_total = 8
    
    if msg1: tests_passed += 1
    if msg2: tests_passed += 1
    if messages_buyer: tests_passed += 1
    if messages_rider: tests_passed += 1
    if unread_buyer is not None: tests_passed += 1
    if unread_rider is not None: tests_passed += 1
    if conversations_buyer: tests_passed += 1
    if conversations_rider: tests_passed += 1
    
    print(f"\n{Colors.BOLD}Tests Passed: {tests_passed}/{tests_total}{Colors.RESET}")
    
    if tests_passed == tests_total:
        print_success("✅ ALL TESTS PASSED!")
    else:
        print_warning(f"⚠️  {tests_total - tests_passed} tests failed")

def setup_test_users():
    """Setup test users by extracting user IDs from tokens"""
    print_header("SETUP: EXTRACTING USER IDs FROM TOKENS")
    
    import jwt
    
    for user_type, user_data in TEST_USERS.items():
        if user_data['token']:
            try:
                # Decode token without verification (just to extract user_id)
                decoded = jwt.decode(user_data['token'], options={"verify_signature": False})
                user_id = decoded.get('user_id')
                if user_id:
                    TEST_USERS[user_type]['id'] = user_id
                    print_success(f"{user_type.capitalize()} ID: {user_id}")
                else:
                    print_error(f"No user_id found in {user_type} token")
            except Exception as e:
                print_error(f"Failed to decode {user_type} token: {e}")
        else:
            print_warning(f"No token set for {user_type}")

def main():
    """Main test runner"""
    print_header("UNIFIED CHAT API TEST SUITE")
    print_info("Testing unified chat system after migration")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test Product ID: {TEST_PRODUCT_ID}")
    print_info(f"Test Order ID: {TEST_ORDER_ID}")
    
    # Check if tokens are set
    if not TEST_USERS['buyer']['token']:
        print_error("BUYER TOKEN NOT SET!")
        print_info("Please update TEST_USERS['buyer']['token'] in the script")
        return
    
    if not TEST_USERS['seller']['token']:
        print_error("SELLER TOKEN NOT SET!")
        print_info("Please update TEST_USERS['seller']['token'] in the script")
        return
    
    if not TEST_USERS['rider']['token']:
        print_warning("RIDER TOKEN NOT SET - Skipping buyer-rider tests")
    
    # Setup: Extract user IDs from tokens
    setup_test_users()
    
    # Run tests
    try:
        # Task 7.1: Buyer-Seller Chat
        test_product_chat()
        
        # Task 7.2: Buyer-Rider Chat (if rider token is set)
        if TEST_USERS['rider']['token']:
            test_order_chat()
        else:
            print_warning("\nSkipping Task 7.2 (Buyer-Rider Chat) - No rider token set")
        
        print_header("ALL TESTS COMPLETE")
        print_success("Review the results above to verify all functionality works correctly")
        
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
