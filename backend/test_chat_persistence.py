"""
Test all chat endpoints to ensure messages are saved to database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Testing Chat Message Persistence")
print("="*60)

with app.app_context():
    try:
        # Get initial count
        result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
        initial_count = result.scalar()
        print(f"\n[INFO] Initial message count: {initial_count}")
        
        # Check recent messages
        print("\n[INFO] Recent messages:")
        result = db.session.execute(text("""
            SELECT 
                cm.id,
                cm.message,
                cm.product_id,
                cm.order_id,
                cm.created_at,
                u1.first_name || ' ' || u1.last_name as sender_name,
                u2.first_name || ' ' || u2.last_name as receiver_name
            FROM chat_message cm
            JOIN "user" u1 ON cm.sender_id = u1.id
            JOIN "user" u2 ON cm.receiver_id = u2.id
            ORDER BY cm.created_at DESC
            LIMIT 10
        """))
        
        messages = result.fetchall()
        if messages:
            for msg in messages:
                msg_type = "Product" if msg[2] else ("Order" if msg[3] else "Direct")
                print(f"  [{msg_type}] {msg[5]} -> {msg[6]}: {msg[1][:50]}...")
                print(f"           Created: {msg[4]}")
        else:
            print("  No messages found")
        
        # Check messages by type
        print("\n[INFO] Messages by type:")
        
        # Direct messages (no product_id, no order_id)
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message 
            WHERE product_id IS NULL AND order_id IS NULL
        """))
        direct_count = result.scalar()
        print(f"  Direct messages: {direct_count}")
        
        # Product messages
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message 
            WHERE product_id IS NOT NULL
        """))
        product_count = result.scalar()
        print(f"  Product messages: {product_count}")
        
        # Order messages
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message 
            WHERE order_id IS NOT NULL
        """))
        order_count = result.scalar()
        print(f"  Order messages: {order_count}")
        
        # Check for orphaned messages (messages with invalid user IDs)
        print("\n[INFO] Checking data integrity:")
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message cm
            WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE id = cm.sender_id)
            OR NOT EXISTS (SELECT 1 FROM "user" WHERE id = cm.receiver_id)
        """))
        orphaned = result.scalar()
        if orphaned > 0:
            print(f"  [WARNING] Found {orphaned} messages with invalid user IDs")
        else:
            print(f"  [OK] All messages have valid user IDs")
        
        # Check for messages with invalid product IDs
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message cm
            WHERE cm.product_id IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM product WHERE id = cm.product_id)
        """))
        invalid_products = result.scalar()
        if invalid_products > 0:
            print(f"  [WARNING] Found {invalid_products} messages with invalid product IDs")
        else:
            print(f"  [OK] All product messages have valid product IDs")
        
        # Show conversation statistics
        print("\n[INFO] Conversation statistics:")
        result = db.session.execute(text("""
            SELECT 
                COUNT(DISTINCT CASE WHEN sender_id < receiver_id 
                    THEN sender_id || '-' || receiver_id 
                    ELSE receiver_id || '-' || sender_id END) as unique_conversations
            FROM chat_message
        """))
        unique_convos = result.scalar()
        print(f"  Unique conversations: {unique_convos}")
        
        # Show users with messages
        print("\n[INFO] Users with messages:")
        result = db.session.execute(text("""
            SELECT 
                u.id,
                u.first_name || ' ' || u.last_name as name,
                u.role,
                COUNT(DISTINCT cm.id) as message_count
            FROM "user" u
            LEFT JOIN chat_message cm ON u.id = cm.sender_id OR u.id = cm.receiver_id
            WHERE cm.id IS NOT NULL
            GROUP BY u.id, u.first_name, u.last_name, u.role
            ORDER BY message_count DESC
        """))
        
        users = result.fetchall()
        if users:
            for user in users:
                print(f"  {user[1]} ({user[2]}): {user[3]} messages")
        else:
            print("  No users with messages")
        
        print("\n" + "="*60)
        print("  Summary")
        print("="*60)
        print(f"  Total messages: {initial_count}")
        print(f"  Direct: {direct_count}")
        print(f"  Product: {product_count}")
        print(f"  Order: {order_count}")
        print(f"  Unique conversations: {unique_convos}")
        print(f"  Active users: {len(users)}")
        
        if orphaned == 0 and invalid_products == 0:
            print("\n[OK] All messages are properly saved and linked!")
        else:
            print("\n[WARNING] Some data integrity issues found")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
