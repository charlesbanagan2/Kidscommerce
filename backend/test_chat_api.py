import requests
import json

# Test the get_messages API
BASE_URL = 'http://192.168.1.26:5000'

# You need to provide a valid JWT token
# Get this from your Flutter app or login first
print("Testing Chat API...")
print("=" * 80)

# First, let's check if we can access the conversations endpoint
# You'll need to replace this with actual JWT token from your app
test_token = input("Enter your JWT access token (from Flutter app): ").strip()

if not test_token:
    print("No token provided. Please login first and get the token.")
    exit()

headers = {
    'Authorization': f'Bearer {test_token}',
    'Content-Type': 'application/json'
}

# Test 1: Get conversations
print("\n1. Testing GET /api/chat/conversations")
print("-" * 80)
response = requests.get(f'{BASE_URL}/api/chat/conversations', headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data.get('success')}")
    conversations = data.get('conversations', [])
    print(f"Total conversations: {len(conversations)}")
    for conv in conversations:
        print(f"\nConversation with User {conv['peer_id']} ({conv['peer_name']}):")
        print(f"  Last message: {conv['last_message']}")
        print(f"  Unread count: {conv['unread_count']}")
        print(f"  Last message time: {conv['last_message_time']}")
else:
    print(f"Error: {response.text}")

# Test 2: Get messages with a specific user
if response.status_code == 200 and conversations:
    other_user_id = conversations[0]['peer_id']
    print(f"\n2. Testing GET /api/chat/messages/{other_user_id}")
    print("-" * 80)
    response = requests.get(f'{BASE_URL}/api/chat/messages/{other_user_id}', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        messages = data.get('messages', [])
        print(f"Total messages: {len(messages)}")
        for msg in messages[:5]:  # Show first 5 messages
            print(f"\nMessage ID: {msg['id']}")
            print(f"  From: {msg['sender_id']} ({msg['sender']['name']})")
            print(f"  To: {msg['receiver_id']}")
            print(f"  Message: {msg['message'][:50]}...")
            print(f"  Time: {msg['created_at']}")
    else:
        print(f"Error: {response.text}")

print("\n" + "=" * 80)
print("Test complete!")
