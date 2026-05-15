"""
Check chat_message table in Supabase database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def check_chat_table():
    """Check if chat_message table exists and show its structure"""
    
    print("="*60)
    print("  CHECKING CHAT_MESSAGE TABLE")
    print("="*60)
    
    with app.app_context():
        try:
            # Check if table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chat_message'
                );
            """))
            
            exists = result.scalar()
            
            if not exists:
                print("\n✗ chat_message table DOES NOT EXIST")
                print("\nTo create it, run:")
                print("  python fix_chat_system.py")
                return False
            
            print("\n✓ chat_message table EXISTS")
            
            # Get table structure
            print("\n" + "="*60)
            print("  TABLE STRUCTURE")
            print("="*60)
            
            result = db.session.execute(text("""
                SELECT 
                    column_name, 
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'chat_message'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("\nColumns:")
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"  {col[0]:20} {col[1]:20} {nullable:10}{default}")
            
            # Get indexes
            print("\n" + "="*60)
            print("  INDEXES")
            print("="*60)
            
            result = db.session.execute(text("""
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE tablename = 'chat_message'
                ORDER BY indexname
            """))
            
            indexes = result.fetchall()
            if indexes:
                print("\nIndexes:")
                for idx in indexes:
                    print(f"  ✓ {idx[0]}")
            else:
                print("\n⚠️  No indexes found")
            
            # Get foreign keys
            print("\n" + "="*60)
            print("  FOREIGN KEYS")
            print("="*60)
            
            result = db.session.execute(text("""
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'chat_message'
            """))
            
            fks = result.fetchall()
            if fks:
                print("\nForeign Keys:")
                for fk in fks:
                    print(f"  ✓ {fk[1]} → {fk[2]}.{fk[3]}")
            else:
                print("\n⚠️  No foreign keys found")
            
            # Get row count
            print("\n" + "="*60)
            print("  DATA")
            print("="*60)
            
            result = db.session.execute(text("SELECT COUNT(*) FROM chat_message"))
            count = result.scalar()
            print(f"\nTotal messages: {count}")
            
            if count > 0:
                # Show recent messages
                result = db.session.execute(text("""
                    SELECT 
                        id,
                        sender_id,
                        receiver_id,
                        LEFT(message, 50) as message_preview,
                        product_id,
                        is_read,
                        created_at
                    FROM chat_message
                    ORDER BY created_at DESC
                    LIMIT 5
                """))
                
                messages = result.fetchall()
                print("\nRecent messages:")
                for msg in messages:
                    read_status = "✓" if msg[5] else "○"
                    product_info = f" [Product #{msg[4]}]" if msg[4] else ""
                    print(f"  {read_status} [{msg[0]}] {msg[1]}→{msg[2]}: {msg[3]}...{product_info}")
            
            # Check RLS policies
            print("\n" + "="*60)
            print("  ROW LEVEL SECURITY")
            print("="*60)
            
            result = db.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    policyname,
                    permissive,
                    roles,
                    cmd
                FROM pg_policies
                WHERE tablename = 'chat_message'
            """))
            
            policies = result.fetchall()
            if policies:
                print("\nRLS Policies:")
                for policy in policies:
                    print(f"  ✓ {policy[2]} ({policy[5]})")
            else:
                print("\n⚠️  No RLS policies found")
            
            # Check if RLS is enabled
            result = db.session.execute(text("""
                SELECT relrowsecurity
                FROM pg_class
                WHERE relname = 'chat_message'
            """))
            
            rls_enabled = result.scalar()
            if rls_enabled:
                print("\n✓ Row Level Security is ENABLED")
            else:
                print("\n⚠️  Row Level Security is DISABLED")
            
            print("\n" + "="*60)
            print("✓ CHAT_MESSAGE TABLE CHECK COMPLETE")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error checking table: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_operations():
    """Test basic operations on chat_message table"""
    
    print("\n" + "="*60)
    print("  TESTING OPERATIONS")
    print("="*60)
    
    with app.app_context():
        try:
            # Get test users
            result = db.session.execute(text("""
                SELECT id, email, role 
                FROM "user" 
                WHERE email IN ('testbuyer@gmail.com', 'testseller@gmail.com')
                LIMIT 2
            """))
            
            users = result.fetchall()
            
            if len(users) < 2:
                print("\n⚠️  Need at least 2 test users")
                print("Run: python fix_chat_system.py")
                return False
            
            sender_id = users[0][0]
            receiver_id = users[1][0]
            
            print(f"\nTest users:")
            print(f"  Sender: {users[0][1]} (ID: {sender_id})")
            print(f"  Receiver: {users[1][1]} (ID: {receiver_id})")
            
            # Test INSERT
            print("\n1. Testing INSERT...")
            result = db.session.execute(text("""
                INSERT INTO chat_message (sender_id, receiver_id, message)
                VALUES (:sender_id, :receiver_id, 'Test message from check script')
                RETURNING id
            """), {'sender_id': sender_id, 'receiver_id': receiver_id})
            
            msg_id = result.scalar()
            db.session.commit()
            print(f"   ✓ Message inserted (ID: {msg_id})")
            
            # Test SELECT
            print("\n2. Testing SELECT...")
            result = db.session.execute(text("""
                SELECT id, sender_id, receiver_id, message, is_read
                FROM chat_message
                WHERE id = :msg_id
            """), {'msg_id': msg_id})
            
            msg = result.fetchone()
            if msg:
                print(f"   ✓ Message retrieved: {msg[3]}")
            
            # Test UPDATE
            print("\n3. Testing UPDATE...")
            db.session.execute(text("""
                UPDATE chat_message
                SET is_read = TRUE
                WHERE id = :msg_id
            """), {'msg_id': msg_id})
            db.session.commit()
            print(f"   ✓ Message marked as read")
            
            # Test DELETE
            print("\n4. Testing DELETE...")
            db.session.execute(text("""
                DELETE FROM chat_message
                WHERE id = :msg_id
            """), {'msg_id': msg_id})
            db.session.commit()
            print(f"   ✓ Message deleted")
            
            print("\n✓ All operations working!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error testing operations: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          CHECK CHAT_MESSAGE TABLE                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check table
    table_exists = check_chat_table()
    
    if table_exists:
        # Test operations
        test_operations()
    else:
        print("\n" + "="*60)
        print("  NEXT STEPS")
        print("="*60)
        print("\n1. Run: python fix_chat_system.py")
        print("2. Restart Flask server")
        print("3. Run: python test_chat_system.py")
        print("="*60)
