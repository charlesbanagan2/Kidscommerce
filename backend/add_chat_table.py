"""
Database Migration: Create ChatMessage Table
Run this script to create the chat_message table
"""

from app import app, db
from sqlalchemy import text

def create_chat_table():
    """Create chat_message table"""
    with app.app_context():
        try:
            # Check if table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'chat_message' in tables:
                print("✅ chat_message table already exists")
                return True
            
            # Create table
            create_table_sql = """
            CREATE TABLE chat_message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES user(id),
                FOREIGN KEY (receiver_id) REFERENCES user(id)
            )
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            
            print("✅ chat_message table created successfully")
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX idx_chat_sender ON chat_message(sender_id)",
                "CREATE INDEX idx_chat_receiver ON chat_message(receiver_id)",
                "CREATE INDEX idx_chat_created ON chat_message(created_at)",
                "CREATE INDEX idx_chat_is_read ON chat_message(is_read)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"✅ Index created: {index_sql.split()[2]}")
                except Exception as e:
                    print(f"⚠️  Index creation warning: {str(e)}")
            
            db.session.commit()
            print("\n✅ Chat system database migration completed!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            return False

if __name__ == '__main__':
    print("Starting chat system database migration...")
    create_chat_table()
