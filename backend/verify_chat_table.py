"""
Verify that the chat_message table exists and is properly configured
"""

from app import app, db
from sqlalchemy import inspect, text

def verify_chat_table():
    """Check if chat_message table exists and show its structure"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("=" * 60)
            print("DATABASE VERIFICATION")
            print("=" * 60)
            print()
            
            # Check if table exists
            if 'chat_message' not in tables:
                print("[ERROR] chat_message table NOT FOUND in database!")
                print(f"Available tables: {', '.join(tables)}")
                return False
            
            print("[OK] chat_message table EXISTS in database")
            print()
            
            # Show table structure
            print("Table Structure:")
            print("-" * 60)
            columns = inspector.get_columns('chat_message')
            for col in columns:
                nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
                default = f" DEFAULT {col.get('default', '')}" if col.get('default') else ""
                print(f"  {col['name']:20} {str(col['type']):20} {nullable}{default}")
            
            print()
            
            # Show foreign keys
            print("Foreign Keys:")
            print("-" * 60)
            fks = inspector.get_foreign_keys('chat_message')
            if fks:
                for fk in fks:
                    print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print("  No foreign keys found")
            
            print()
            
            # Show indexes
            print("Indexes:")
            print("-" * 60)
            indexes = inspector.get_indexes('chat_message')
            if indexes:
                for idx in indexes:
                    cols = ', '.join(idx['column_names'])
                    unique = " (UNIQUE)" if idx.get('unique') else ""
                    print(f"  {idx['name']:30} on ({cols}){unique}")
            else:
                print("  No indexes found")
            
            print()
            
            # Test insert and query
            print("Testing Database Operations:")
            print("-" * 60)
            
            # Count existing messages
            result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
            count = result.scalar()
            print(f"  Current message count: {count}")
            
            # Test that we can query the table
            result = db.session.execute(text("SELECT * FROM chat_message LIMIT 1"))
            print(f"  [OK] Table is queryable")
            
            print()
            print("=" * 60)
            print("[SUCCESS] chat_message table is properly configured!")
            print("=" * 60)
            print()
            print("Available API Endpoints:")
            print("  GET  /api/chat/conversations")
            print("  GET  /api/chat/messages/<user_id>")
            print("  POST /api/chat/send")
            print("  GET  /api/chat/unread-count")
            print()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    verify_chat_table()
