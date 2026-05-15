"""
Create chat_message table in Supabase PostgreSQL database
Run this script to set up the chat system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def create_chat_table():
    """Create chat_message table with proper indexes and RLS policies"""
    
    print("="*60)
    print("  Creating chat_message table in Supabase")
    print("="*60)
    
    with app.app_context():
        try:
            # Check if table already exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chat_message'
                );
            """))
            
            exists = result.scalar()
            
            if exists:
                print("\n⚠️  chat_message table already exists")
                response = input("Drop and recreate? (y/n): ").lower()
                if response != 'y':
                    print("Aborted.")
                    return
                
                print("\nDropping existing table...")
                db.session.execute(text("DROP TABLE IF EXISTS chat_message CASCADE"))
                db.session.commit()
                print("✓ Table dropped")
            
            print("\nCreating chat_message table...")
            
            # Create table
            db.session.execute(text("""
                CREATE TABLE chat_message (
                    id SERIAL PRIMARY KEY,
                    sender_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    receiver_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    product_id INTEGER REFERENCES product(id) ON DELETE SET NULL,
                    order_id INTEGER REFERENCES "order"(id) ON DELETE SET NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            db.session.commit()
            print("✓ Table created")
            
            print("\nCreating indexes...")
            
            # Create indexes
            indexes = [
                "CREATE INDEX idx_chat_message_sender ON chat_message(sender_id)",
                "CREATE INDEX idx_chat_message_receiver ON chat_message(receiver_id)",
                "CREATE INDEX idx_chat_message_product ON chat_message(product_id)",
                "CREATE INDEX idx_chat_message_order ON chat_message(order_id)",
                "CREATE INDEX idx_chat_message_created_at ON chat_message(created_at DESC)",
                "CREATE INDEX idx_chat_message_unread ON chat_message(receiver_id, is_read) WHERE is_read = FALSE",
                "CREATE INDEX idx_chat_message_conversation ON chat_message(sender_id, receiver_id, created_at DESC)",
                "CREATE INDEX idx_chat_message_product_conversation ON chat_message(product_id, sender_id, receiver_id, created_at DESC)"
            ]
            
            for idx_sql in indexes:
                try:
                    db.session.execute(text(idx_sql))
                    db.session.commit()
                    print(f"  ✓ {idx_sql.split('INDEX ')[1].split(' ON')[0]}")
                except Exception as e:
                    print(f"  ⚠️  Index creation warning: {e}")
            
            print("\nEnabling Row Level Security...")
            
            # Enable RLS
            db.session.execute(text("ALTER TABLE chat_message ENABLE ROW LEVEL SECURITY"))
            db.session.commit()
            print("✓ RLS enabled")
            
            print("\nCreating RLS policies...")
            
            # Drop existing policies if any
            try:
                db.session.execute(text("""
                    DROP POLICY IF EXISTS "Users can view their own messages" ON chat_message;
                    DROP POLICY IF EXISTS "Users can send messages" ON chat_message;
                    DROP POLICY IF EXISTS "Users can mark received messages as read" ON chat_message;
                """))
                db.session.commit()
            except:
                pass
            
            # Create RLS policies
            policies = [
                """
                CREATE POLICY "Users can view their own messages"
                ON chat_message
                FOR SELECT
                USING (
                    sender_id = current_setting('request.jwt.claims', true)::json->>'user_id'::text::integer
                    OR receiver_id = current_setting('request.jwt.claims', true)::json->>'user_id'::text::integer
                )
                """,
                """
                CREATE POLICY "Users can send messages"
                ON chat_message
                FOR INSERT
                WITH CHECK (sender_id = current_setting('request.jwt.claims', true)::json->>'user_id'::text::integer)
                """,
                """
                CREATE POLICY "Users can mark received messages as read"
                ON chat_message
                FOR UPDATE
                USING (receiver_id = current_setting('request.jwt.claims', true)::json->>'user_id'::text::integer)
                WITH CHECK (receiver_id = current_setting('request.jwt.claims', true)::json->>'user_id'::text::integer)
                """
            ]
            
            for policy_sql in policies:
                try:
                    db.session.execute(text(policy_sql))
                    db.session.commit()
                    policy_name = policy_sql.split('"')[1]
                    print(f"  ✓ {policy_name}")
                except Exception as e:
                    print(f"  ⚠️  Policy creation warning: {e}")
            
            print("\nGranting permissions...")
            
            # Grant permissions
            try:
                db.session.execute(text("""
                    GRANT ALL ON chat_message TO authenticated;
                    GRANT ALL ON chat_message TO anon;
                    GRANT USAGE, SELECT ON SEQUENCE chat_message_id_seq TO authenticated;
                    GRANT USAGE, SELECT ON SEQUENCE chat_message_id_seq TO anon;
                """))
                db.session.commit()
                print("✓ Permissions granted")
            except Exception as e:
                print(f"  ⚠️  Permission warning: {e}")
            
            print("\nVerifying table...")
            
            # Verify
            result = db.session.execute(text("""
                SELECT 
                    table_name,
                    (SELECT COUNT(*) FROM chat_message) as message_count
                FROM information_schema.tables 
                WHERE table_name = 'chat_message'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✓ Table verified: {row[0]}")
                print(f"✓ Current messages: {row[1]}")
            
            print("\n" + "="*60)
            print("✓ Chat system database setup complete!")
            print("="*60)
            print("\nNext steps:")
            print("1. Restart your Flask server")
            print("2. Run: python test_chat_system.py")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error creating table: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure Supabase connection is working")
            print("2. Check if user and product tables exist")
            print("3. Verify database permissions")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_chat_table()
