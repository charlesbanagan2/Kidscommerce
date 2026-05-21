"""
SocketIO Event Testing Script
Tests real-time messaging events for Task 8.1
"""

import socketio
import time
import requests
import json
from threading import Thread, Event

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Test tokens (from previous test)
BUYER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwicm9sZSI6ImJ1eWVyIiwiZXhwIjoxNzgxOTM5NDU5fQ.iYEhbyhwC5Ntz20NDv0VlhHGWisWnIU73ErhlI-sLl0'
SELLER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwicm9sZSI6InNlbGxlciIsImV4cCI6MTc4MTkzOTQ1OX0.PYiLTC5TeC_2bI_ofAGMfopMUerJR8W9DZ9eup-PO3g'

BUYER_ID = 10
SELLER_ID = 11

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

def print_event(event_name, data):
    print(f"{Colors.YELLOW}📡 Event received: {event_name}{Colors.RESET}")
    print(f"   Data: {json.dumps(data, indent=2)}")

class SocketIOTester:
    def __init__(self, user_type, token, user_id):
        self.user_type = user_type
        self.token = token
        self.user_id = user_id
        self.sio = socketio.Client()
        self.events_received = []
        self.connected = Event()
        self.joined = Event()
        
        # Register event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('joined_chat', self.on_joined_chat)
        self.sio.on('new_message', self.on_new_message)
        self.sio.on('user_typing', self.on_user_typing)
        self.sio.on('user_stop_typing', self.on_user_stop_typing)
        self.sio.on('conversation_updated', self.on_conversation_updated)
        self.sio.on('unread_cleared', self.on_unread_cleared)
    
    def on_connect(self):
        print_success(f"{self.user_type.capitalize()} connected to SocketIO")
        self.connected.set()
    
    def on_disconnect(self):
        print_info(f"{self.user_type.capitalize()} disconnected from SocketIO")
    
    def on_joined_chat(self, data):
        print_event('joined_chat', data)
        self.events_received.append(('joined_chat', data))
        self.joined.set()
    
    def on_new_message(self, data):
        print_event('new_message', data)
        self.events_received.append(('new_message', data))
    
    def on_user_typing(self, data):
        print_event('user_typing', data)
        self.events_received.append(('user_typing', data))
    
    def on_user_stop_typing(self, data):
        print_event('user_stop_typing', data)
        self.events_received.append(('user_stop_typing', data))
    
    def on_conversation_updated(self, data):
        print_event('conversation_updated', data)
        self.events_received.append(('conversation_updated', data))
    
    def on_unread_cleared(self, data):
        print_event('unread_cleared', data)
        self.events_received.append(('unread_cleared', data))
    
    def connect(self):
        """Connect to SocketIO server"""
        try:
            # Note: Flask-SocketIO doesn't support auth parameter in the same way
            # We'll need to send the token after connecting
            self.sio.connect(BASE_URL, wait_timeout=10)
            
            # Wait for connection
            if self.connected.wait(timeout=5):
                print_success(f"{self.user_type.capitalize()} connection established")
                return True
            else:
                print_error(f"{self.user_type.capitalize()} connection timeout")
                return False
        except Exception as e:
            print_error(f"{self.user_type.capitalize()} connection failed: {e}")
            return False
    
    def join_chat(self):
        """Join chat room"""
        try:
            self.sio.emit('join_chat', {})
            
            # Wait for joined confirmation
            if self.joined.wait(timeout=5):
                print_success(f"{self.user_type.capitalize()} joined chat room")
                return True
            else:
                print_error(f"{self.user_type.capitalize()} join timeout")
                return False
        except Exception as e:
            print_error(f"{self.user_type.capitalize()} join failed: {e}")
            return False
    
    def send_typing(self, receiver_id):
        """Send typing indicator"""
        try:
            self.sio.emit('typing', {'receiver_id': receiver_id})
            print_info(f"{self.user_type.capitalize()} sent typing indicator to user {receiver_id}")
            return True
        except Exception as e:
            print_error(f"{self.user_type.capitalize()} typing emit failed: {e}")
            return False
    
    def send_stop_typing(self, receiver_id):
        """Send stop typing indicator"""
        try:
            self.sio.emit('stop_typing', {'receiver_id': receiver_id})
            print_info(f"{self.user_type.capitalize()} sent stop_typing indicator to user {receiver_id}")
            return True
        except Exception as e:
            print_error(f"{self.user_type.capitalize()} stop_typing emit failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SocketIO"""
        try:
            self.sio.disconnect()
            print_info(f"{self.user_type.capitalize()} disconnected")
        except Exception as e:
            print_error(f"{self.user_type.capitalize()} disconnect failed: {e}")
    
    def get_event_count(self, event_name):
        """Get count of specific event received"""
        return len([e for e in self.events_received if e[0] == event_name])

def send_message_via_api(sender_token, receiver_id, message):
    """Send a message via REST API"""
    try:
        response = requests.post(
            f"{API_BASE}/chat/send",
            headers={
                'Authorization': f'Bearer {sender_token}',
                'Content-Type': 'application/json'
            },
            json={
                'receiver_id': receiver_id,
                'message': message
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print_success(f"Message sent via API: {message[:30]}...")
                return data['message']
        
        print_error(f"API send failed: {response.status_code}")
        return None
    except Exception as e:
        print_error(f"API send exception: {e}")
        return None

def test_socketio_events():
    """Test all SocketIO events"""
    print_header("TASK 8.1: SOCKETIO EVENT TESTING")
    
    tests_passed = 0
    tests_total = 8
    
    # Create testers
    buyer_tester = SocketIOTester('buyer', BUYER_TOKEN, BUYER_ID)
    seller_tester = SocketIOTester('seller', SELLER_TOKEN, SELLER_ID)
    
    try:
        # Test 1: Connect both users
        print_info("\n[Test 1] Connecting users to SocketIO...")
        buyer_connected = buyer_tester.connect()
        seller_connected = seller_tester.connect()
        
        if buyer_connected and seller_connected:
            print_success("Test 1 PASSED: Both users connected")
            tests_passed += 1
        else:
            print_error("Test 1 FAILED: Connection issues")
        
        time.sleep(1)
        
        # Test 2: Join chat rooms
        print_info("\n[Test 2] Joining chat rooms...")
        buyer_joined = buyer_tester.join_chat()
        seller_joined = seller_tester.join_chat()
        
        if buyer_joined and seller_joined:
            print_success("Test 2 PASSED: Both users joined chat rooms")
            tests_passed += 1
        else:
            print_error("Test 2 FAILED: Join issues")
        
        time.sleep(1)
        
        # Test 3: Send message and verify new_message event
        print_info("\n[Test 3] Testing new_message event...")
        buyer_tester.events_received.clear()
        seller_tester.events_received.clear()
        
        msg = send_message_via_api(BUYER_TOKEN, SELLER_ID, "Test message for SocketIO event")
        time.sleep(2)  # Wait for event propagation
        
        seller_new_msg_count = seller_tester.get_event_count('new_message')
        if seller_new_msg_count > 0:
            print_success(f"Test 3 PASSED: Seller received {seller_new_msg_count} new_message event(s)")
            tests_passed += 1
        else:
            print_error("Test 3 FAILED: Seller did not receive new_message event")
        
        # Test 4: Verify conversation_updated event
        print_info("\n[Test 4] Testing conversation_updated event...")
        buyer_conv_count = buyer_tester.get_event_count('conversation_updated')
        seller_conv_count = seller_tester.get_event_count('conversation_updated')
        
        if buyer_conv_count > 0 or seller_conv_count > 0:
            print_success(f"Test 4 PASSED: conversation_updated events received (buyer: {buyer_conv_count}, seller: {seller_conv_count})")
            tests_passed += 1
        else:
            print_error("Test 4 FAILED: No conversation_updated events received")
        
        time.sleep(1)
        
        # Test 5: Test typing indicator
        print_info("\n[Test 5] Testing typing indicator...")
        seller_tester.events_received.clear()
        
        buyer_tester.send_typing(SELLER_ID)
        time.sleep(2)
        
        seller_typing_count = seller_tester.get_event_count('user_typing')
        if seller_typing_count > 0:
            print_success(f"Test 5 PASSED: Seller received {seller_typing_count} user_typing event(s)")
            tests_passed += 1
        else:
            print_error("Test 5 FAILED: Seller did not receive user_typing event")
        
        # Test 6: Test stop_typing indicator
        print_info("\n[Test 6] Testing stop_typing indicator...")
        seller_tester.events_received.clear()
        
        buyer_tester.send_stop_typing(SELLER_ID)
        time.sleep(2)
        
        seller_stop_typing_count = seller_tester.get_event_count('user_stop_typing')
        if seller_stop_typing_count > 0:
            print_success(f"Test 6 PASSED: Seller received {seller_stop_typing_count} user_stop_typing event(s)")
            tests_passed += 1
        else:
            print_error("Test 6 FAILED: Seller did not receive user_stop_typing event")
        
        # Test 7: Test persistent connections
        print_info("\n[Test 7] Testing persistent connections...")
        time.sleep(3)
        
        if buyer_tester.sio.connected and seller_tester.sio.connected:
            print_success("Test 7 PASSED: Connections remain persistent")
            tests_passed += 1
        else:
            print_error("Test 7 FAILED: Connections dropped")
        
        # Test 8: Test concurrent messages
        print_info("\n[Test 8] Testing concurrent message handling...")
        buyer_tester.events_received.clear()
        seller_tester.events_received.clear()
        
        # Send multiple messages quickly
        for i in range(3):
            send_message_via_api(BUYER_TOKEN, SELLER_ID, f"Concurrent message {i+1}")
            time.sleep(0.1)
        
        time.sleep(2)
        
        seller_msg_count = seller_tester.get_event_count('new_message')
        if seller_msg_count >= 3:
            print_success(f"Test 8 PASSED: Seller received {seller_msg_count} concurrent messages")
            tests_passed += 1
        else:
            print_error(f"Test 8 FAILED: Seller only received {seller_msg_count}/3 messages")
        
    except Exception as e:
        print_error(f"Test exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print_info("\nCleaning up connections...")
        buyer_tester.disconnect()
        seller_tester.disconnect()
    
    # Summary
    print_header("TASK 8.1 SUMMARY")
    print(f"\n{Colors.BOLD}Tests Passed: {tests_passed}/{tests_total}{Colors.RESET}")
    
    if tests_passed == tests_total:
        print_success("✅ ALL SOCKETIO TESTS PASSED!")
    else:
        print_error(f"❌ {tests_total - tests_passed} tests failed")
    
    return tests_passed == tests_total

if __name__ == '__main__':
    try:
        success = test_socketio_events()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_info("\n\nTests interrupted by user")
        exit(1)
