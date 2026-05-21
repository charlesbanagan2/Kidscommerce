"""
Comprehensive Chat System Debug Script
Tests all chat endpoints and database queries
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sys

load_dotenv()

print("=" * 80)
print("CHAT SYSTEM COMPREHENSIVE DEBUG")
print("=" * 80)

engine = create_engine(os.getenv('SUPABASE_DB_URL'))

# Test 1: Check chat_message table structure
print("\n1. CHECKING CHAT_MESSAGE TABLE STRUCTURE")
print("-" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'chat_message'
        ORDER BY ordinal_position
    """))
    print("Columns:")
    for row in result:
        print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")

# Test 2: Check total messages
print("\n2. CHECKING TOTAL MESSAGES")
print("-" * 80)
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM chat_message'))
    total = result.fetchone()[0]
    print(f"Total messages in database: {total}")

# Test 3: Check messages by user pairs
print("\n3. CHECKING MESSAGES BY USER PAIRS")
print("-" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            LEAST(sender_id, receiver_id) as user1,
            GREATEST(sender_id, receiver_id) as user2,
            COUNT(*) as total_messages,
            MAX(created_at) as last_message_time
        FROM chat_message
        GROUP BY user1, user2
        ORDER BY last_message_time DESC
    """))
    print("Conversations (both directions combined):")
    for row in result:
        print(f"  User {row[0]} <-> User {row[1]}: {row[2]} messages (last: {row[3]})")

# Test 4: Check specific user's conversations
print("\n4. CHECKING SPECIFIC USER'S CONVERSATIONS")
print("-" * 80)
user_id = input("Enter user ID to check (or press Enter to skip): ").strip()
if user_id:
    user_id = int(user_id)
    with engine.connect() as conn:
        # Get all users this user has chatted with
        result = conn.execute(text("""
            SELECT DISTINCT
                CASE 
                    WHEN sender_id = :user_id THEN receiver_id
                    ELSE sender_id
                END as other_user_id
            FROM chat_message
            WHERE sender_id = :user_id OR receiver_id = :user_id
        """), {'user_id': user_id})
        
        other_users = [row[0] for row in result]
        print(f"\nUser {user_id} has conversations with {len(other_users)} users:")
        
        for other_id in other_users:
            # Get message count
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM chat_message
                WHERE (sender_id = :user_id AND receiver_id = :other_id)
                   OR (sender_id = :other_id AND receiver_id = :user_id)
            """), {'user_id': user_id, 'other_id': other_id})
            count = result.fetchone()[0]
            
            # Get last message
            result = conn.execute(text("""
                SELECT message, created_at, sender_id
                FROM chat_message
                WHERE (sender_id = :user_id AND receiver_id = :other_id)
                   OR (sender_id = :other_id AND receiver_id = :user_id)
                ORDER BY created_at DESC
                LIMIT 1
            """), {'user_id': user_id, 'other_id': other_id})
            last_msg = result.fetchone()
            
            print(f"\n  With User {other_id}:")
            print(f"    Total messages: {count}")
            if last_msg:
                msg_preview = last_msg[0][:50] if len(last_msg[0]) > 50 else last_msg[0]
                sender = "You" if last_msg[2] == user_id else f"User {other_id}"
                print(f"    Last message: {msg_preview}")
                print(f"    From: {sender}")
                print(f"    Time: {last_msg[1]}")

# Test 5: Check for orphaned messages (users that don't exist)
print("\n5. CHECKING FOR ORPHANED MESSAGES")
print("-" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT DISTINCT cm.sender_id
        FROM chat_message cm
        LEFT JOIN "user" u ON cm.sender_id = u.id
        WHERE u.id IS NULL
    """))
    orphaned_senders = [row[0] for row in result]
    
    result = conn.execute(text("""
        SELECT DISTINCT cm.receiver_id
        FROM chat_message cm
        LEFT JOIN "user" u ON cm.receiver_id = u.id
        WHERE u.id IS NULL
    """))
    orphaned_receivers = [row[0] for row in result]
    
    if orphaned_senders or orphaned_receivers:
        print("WARNING: Found orphaned messages!")
        if orphaned_senders:
            print(f"  Senders not in user table: {orphaned_senders}")
        if orphaned_receivers:
            print(f"  Receivers not in user table: {orphaned_receivers}")
    else:
        print("OK: No orphaned messages found")

# Test 6: Test the exact query used by get_messages endpoint
print("\n6. TESTING GET_MESSAGES QUERY")
print("-" * 80)
test_user1 = input("Enter first user ID (or press Enter to skip): ").strip()
test_user2 = input("Enter second user ID (or press Enter to skip): ").strip()

if test_user1 and test_user2:
    test_user1 = int(test_user1)
    test_user2 = int(test_user2)
    
    with engine.connect() as conn:
        # This is the exact query from get_messages endpoint
        result = conn.execute(text("""
            SELECT id, sender_id, receiver_id, message, is_read, created_at, product_id
            FROM chat_message
            WHERE (sender_id = :user1 AND receiver_id = :user2)
               OR (sender_id = :user2 AND receiver_id = :user1)
            ORDER BY created_at ASC
        """), {'user1': test_user1, 'user2': test_user2})
        
        messages = result.fetchall()
        print(f"\nFound {len(messages)} messages between User {test_user1} and User {test_user2}:")
        
        for msg in messages:
            msg_preview = msg[3][:50] if len(msg[3]) > 50 else msg[3]
            direction = f"{msg[1]} -> {msg[2]}"
            read_status = "READ" if msg[4] else "UNREAD"
            print(f"\n  ID {msg[0]}: {direction} ({read_status})")
            print(f"    Message: {msg_preview}")
            print(f"    Time: {msg[5]}")
            if msg[6]:
                print(f"    Product ID: {msg[6]}")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
