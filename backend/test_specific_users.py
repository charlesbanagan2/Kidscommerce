"""
Test get_messages query for User 25 (buyer) and User 14 (seller)
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('SUPABASE_DB_URL'))

# Test User 25 viewing messages with User 14
user_id = 25  # Buyer
other_user_id = 14  # Seller

print("=" * 80)
print(f"TESTING: User {user_id} viewing messages with User {other_user_id}")
print("=" * 80)

with engine.connect() as conn:
    # This is the EXACT query from get_messages endpoint
    result = conn.execute(text("""
        SELECT id, sender_id, receiver_id, message, is_read, created_at, product_id
        FROM chat_message
        WHERE (sender_id = :user_id AND receiver_id = :other_user_id)
           OR (sender_id = :other_user_id AND receiver_id = :user_id)
        ORDER BY created_at ASC
    """), {'user_id': user_id, 'other_user_id': other_user_id})
    
    messages = result.fetchall()
    print(f"\nQuery returned {len(messages)} messages:")
    print("-" * 80)
    
    for i, msg in enumerate(messages, 1):
        direction = "SENT" if msg[1] == user_id else "RECEIVED"
        read_status = "READ" if msg[4] else "UNREAD"
        print(f"\n{i}. Message ID: {msg[0]} ({direction}, {read_status})")
        print(f"   From: User {msg[1]} -> To: User {msg[2]}")
        print(f"   Message: {msg[3]}")
        print(f"   Time: {msg[5]}")
        if msg[6]:
            print(f"   Product ID: {msg[6]}")

# Now test the reverse (User 14 viewing messages with User 25)
print("\n" + "=" * 80)
print(f"TESTING: User {other_user_id} viewing messages with User {user_id}")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, sender_id, receiver_id, message, is_read, created_at, product_id
        FROM chat_message
        WHERE (sender_id = :user_id AND receiver_id = :other_user_id)
           OR (sender_id = :other_user_id AND receiver_id = :user_id)
        ORDER BY created_at ASC
    """), {'user_id': other_user_id, 'other_user_id': user_id})
    
    messages = result.fetchall()
    print(f"\nQuery returned {len(messages)} messages:")
    print("-" * 80)
    
    for i, msg in enumerate(messages, 1):
        direction = "SENT" if msg[1] == other_user_id else "RECEIVED"
        read_status = "READ" if msg[4] else "UNREAD"
        print(f"\n{i}. Message ID: {msg[0]} ({direction}, {read_status})")
        print(f"   From: User {msg[1]} -> To: User {msg[2]}")
        print(f"   Message: {msg[3]}")
        print(f"   Time: {msg[5]}")
        if msg[6]:
            print(f"   Product ID: {msg[6]}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("Both queries should return the SAME messages (just different perspective)")
print("If Flutter app shows 0 messages, the problem is NOT in the database query.")
print("Check:")
print("1. Is the JWT token valid?")
print("2. Is the user_id extracted correctly from token?")
print("3. Is the API endpoint being called correctly?")
print("4. Check backend logs for errors")
