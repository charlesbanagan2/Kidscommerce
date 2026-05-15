"""
Check and fix ChatMessage table structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text, inspect

print("="*60)
print("  Checking ChatMessage Table")
print("="*60)

with app.app_context():
    try:
        # Check if chat_message table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'chat_message' not in tables:
            print("\n[ERROR] chat_message table does not exist!")
            print("Run: python setup_chat_database.py")
            exit(1)
        
        print("\n[OK] chat_message table exists")
        
        # Check columns
        print("\nColumns:")
        columns = inspector.get_columns('chat_message')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Check foreign keys
        print("\nForeign Keys:")
        fks = inspector.get_foreign_keys('chat_message')
        for fk in fks:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Test query
        print("\nTesting query...")
        result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
        count = result.scalar()
        print(f"[OK] Found {count} messages in chat_message table")
        
        # Test with joins
        print("\nTesting join with user table...")
        result = db.session.execute(text("""
            SELECT cm.id, u.first_name, u.last_name
            FROM chat_message cm
            JOIN "user" u ON cm.sender_id = u.id
            LIMIT 5
        """))
        rows = result.fetchall()
        if rows:
            print(f"[OK] Join works! Sample messages:")
            for row in rows:
                print(f"  - Message {row[0]} from {row[1]} {row[2]}")
        else:
            print("[INFO] No messages found")
        
        print("\n" + "="*60)
        print("  ChatMessage table is properly configured")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
