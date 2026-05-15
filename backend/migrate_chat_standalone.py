"""
Database Migration: Create Unified ChatMessage Table
Standalone script - no app.py import needed
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
SUPABASE_ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'mobile_app',
    'lib',
    'kids_commercedb',
    'supabase.env',
)
load_dotenv(SUPABASE_ENV_PATH, override=True)

def get_db_url():
    """Get database URL from environment"""
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip()
    
    if SUPABASE_DB_URL:
        return SUPABASE_DB_URL
    
    # Build from components
    supabase_project_ref = SUPABASE_URL.replace('https://', '').split('.')[0]
    db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
    db_password = os.getenv('SUPABASE_DB_PASSWORD', '').strip()
    db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
    db_host = os.getenv('SUPABASE_DB_HOST', f"db.{supabase_project_ref}.supabase.co")
    db_port = os.getenv('SUPABASE_DB_PORT', '6543')
    
    if db_password:
        return f"postgresql+psycopg2://{db_user}:{quote(db_password, safe='')}@{db_host}:{db_port}/{db_name}"
    
    raise RuntimeError('Missing database configuration')

def migrate_chat_system():
    """Create unified chat_message table"""
    try:
        db_url = get_db_url()
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Check if table already exists
            if 'chat_message' in tables:
                print("✅ chat_message table already exists")
                return True
            
            print("📦 Creating chat_message table...")
            
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
            
            conn.execute(text(create_table_sql))
            conn.commit()
            
            print("✅ chat_message table created successfully")
            
            # Create indexes for better performance
            print("📦 Creating indexes...")
            
            indexes = [
                "CREATE INDEX idx_chat_sender ON chat_message(sender_id)",
                "CREATE INDEX idx_chat_receiver ON chat_message(receiver_id)",
                "CREATE INDEX idx_chat_created ON chat_message(created_at DESC)",
                "CREATE INDEX idx_chat_is_read ON chat_message(is_read) WHERE is_read = FALSE",
                "CREATE INDEX idx_chat_conversation ON chat_message(sender_id, receiver_id, created_at DESC)"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    print(f"✅ Index created: {index_sql.split()[2]}")
                except Exception as e:
                    print(f"⚠️ Index creation warning: {str(e)}")
            
            conn.commit()
            
            print("\n✅ Chat system database migration completed!")
            print("\n📋 Next steps:")
            print("1. Update app.py - Find line 88: register_notification_api(app)")
            print("   Change to: register_notification_api(app, db, Notification, User)")
            print("\n2. Add unified chat to app.py AFTER socketio initialization:")
            print("   from unified_chat_api import register_unified_chat")
            print("   register_unified_chat(app, db, socketio)")
            print("\n3. Restart your Flask server: python app.py")
            print("\n4. Test the chat endpoints:")
            print("   GET  /api/chat/conversations")
            print("   GET  /api/chat/messages/<user_id>")
            print("   POST /api/chat/send")
            print("   GET  /api/chat/unread-count")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("UNIFIED CHAT SYSTEM - DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    success = migrate_chat_system()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED")
        print("=" * 60)
