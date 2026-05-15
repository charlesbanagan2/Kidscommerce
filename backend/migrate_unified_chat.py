"""
Database Migration: Create Unified ChatMessage Table
Run this script to create the chat_message table for the unified chat system
"""

from app import app, db
from sqlalchemy import text, inspect

def migrate_chat_system():
    """Create unified chat_message table"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Check if table already exists
            if 'chat_message' in tables:
                print("[OK] chat_message table already exists")
                return True
            
            print("[INFO] Creating chat_message table...")
            
            # Create table (PostgreSQL compatible)
            create_table_sql = """
            CREATE TABLE chat_message (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER NOT NULL REFERENCES "user"(id),
                receiver_id INTEGER NOT NULL REFERENCES "user"(id),
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            
            print("[OK] chat_message table created successfully")
            
            # Create indexes for better performance
            print("[INFO] Creating indexes...")
            
            indexes = [
                "CREATE INDEX idx_chat_sender ON chat_message(sender_id)",
                "CREATE INDEX idx_chat_receiver ON chat_message(receiver_id)",
                "CREATE INDEX idx_chat_created ON chat_message(created_at DESC)",
                "CREATE INDEX idx_chat_is_read ON chat_message(is_read) WHERE is_read = FALSE",
                "CREATE INDEX idx_chat_conversation ON chat_message(sender_id, receiver_id, created_at DESC)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"[OK] Index created: {index_sql.split()[2]}")
                except Exception as e:
                    print(f"[WARNING] Index creation warning: {str(e)}")
            
            db.session.commit()
            
            print("\n[OK] Chat system database migration completed!")
            print("\n[INFO] Next steps:")
            print("1. Add this line to app.py after socketio initialization:")
            print("   from unified_chat_api import register_unified_chat")
            print("   register_unified_chat(app, db, socketio)")
            print("\n2. Restart your Flask server")
            print("\n3. Test the chat endpoints:")
            print("   GET  /api/chat/conversations")
            print("   GET  /api/chat/messages/<user_id>")
            print("   POST /api/chat/send")
            print("   GET  /api/chat/unread-count")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error during migration: {str(e)}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("UNIFIED CHAT SYSTEM - DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    success = migrate_chat_system()
    
    if success:
        print("\n" + "=" * 60)
        print("[OK] MIGRATION SUCCESSFUL")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] MIGRATION FAILED")
        print("=" * 60)
