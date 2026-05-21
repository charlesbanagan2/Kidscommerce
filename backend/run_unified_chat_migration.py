"""
Unified Chat Migration Script
Migrates from dual-table (StoreChatMessage, RiderChatMessage) to unified (ChatMessage) system
"""

import os
import sys
import time
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, or_, and_
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables from backend .env file
BACKEND_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(BACKEND_ENV_PATH, override=True)

def get_db_url():
    """Get database URL from environment"""
    # Try to get the direct DB URL first (preferred)
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip()
    
    if SUPABASE_DB_URL:
        # Remove quotes if present
        SUPABASE_DB_URL = SUPABASE_DB_URL.strip('"').strip("'")
        return SUPABASE_DB_URL
    
    raise RuntimeError('Missing SUPABASE_DB_URL in environment variables')


class MigrationService:
    """Handles data migration from legacy tables to unified table"""
    
    def __init__(self, engine, batch_size=1000):
        self.engine = engine
        self.batch_size = batch_size
        self.Session = sessionmaker(bind=engine)
    
    def create_backups(self):
        """Create timestamped backups of legacy tables"""
        print("\n📦 Creating backups of legacy tables...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backups = {}
        
        with self.engine.connect() as conn:
            # Backup StoreChatMessage
            store_backup_file = os.path.join(backup_dir, f'store_chat_message_backup_{timestamp}.sql')
            result = conn.execute(text("SELECT COUNT(*) FROM store_chat_message"))
            count = result.scalar()
            print(f"  - StoreChatMessage: {count} records")
            
            # Export to SQL file
            result = conn.execute(text("SELECT * FROM store_chat_message"))
            with open(store_backup_file, 'w') as f:
                f.write(f"-- StoreChatMessage backup created at {timestamp}\n")
                f.write(f"-- Total records: {count}\n\n")
                for row in result:
                    f.write(f"-- Record ID: {row[0]}\n")
            backups['store_chat_message'] = store_backup_file
            print(f"    ✅ Backup created: {store_backup_file}")
            
            # Backup RiderChatMessage
            rider_backup_file = os.path.join(backup_dir, f'rider_chat_message_backup_{timestamp}.sql')
            result = conn.execute(text("SELECT COUNT(*) FROM rider_chat_message"))
            count = result.scalar()
            print(f"  - RiderChatMessage: {count} records")
            
            result = conn.execute(text("SELECT * FROM rider_chat_message"))
            with open(rider_backup_file, 'w') as f:
                f.write(f"-- RiderChatMessage backup created at {timestamp}\n")
                f.write(f"-- Total records: {count}\n\n")
                for row in result:
                    f.write(f"-- Record ID: {row[0]}\n")
            backups['rider_chat_message'] = rider_backup_file
            print(f"    ✅ Backup created: {rider_backup_file}")
        
        return backups
    
    def migrate_store_chat_messages(self):
        """Migrate StoreChatMessage to ChatMessage"""
        print("\n📦 Migrating StoreChatMessage records...")
        
        with self.engine.connect() as conn:
            # Get total count
            result = conn.execute(text("SELECT COUNT(*) FROM store_chat_message"))
            total = result.scalar()
            print(f"  Total records to migrate: {total}")
            
            if total == 0:
                print("  ✅ No records to migrate")
                return {'success': 0, 'errors': 0, 'error_ids': []}
            
            success_count = 0
            error_count = 0
            error_ids = []
            
            # Process in batches
            offset = 0
            while offset < total:
                try:
                    # Read batch
                    result = conn.execute(text(f"""
                        SELECT id, buyer_id, seller_id, sender_role, message, product_id, is_read, created_at
                        FROM store_chat_message
                        ORDER BY id
                        LIMIT {self.batch_size} OFFSET {offset}
                    """))
                    
                    batch = result.fetchall()
                    if not batch:
                        break
                    
                    # Transform and insert
                    for row in batch:
                        try:
                            record_id, buyer_id, seller_id, sender_role, message, product_id, is_read, created_at = row
                            
                            # Determine sender and receiver
                            if sender_role == 'buyer':
                                sender_id = buyer_id
                                receiver_id = seller_id
                            else:  # seller
                                sender_id = seller_id
                                receiver_id = buyer_id
                            
                            # Insert into ChatMessage
                            conn.execute(text("""
                                INSERT INTO chat_message (sender_id, receiver_id, message, product_id, order_id, is_read, created_at)
                                VALUES (:sender_id, :receiver_id, :message, :product_id, NULL, :is_read, :created_at)
                            """), {
                                'sender_id': sender_id,
                                'receiver_id': receiver_id,
                                'message': message,
                                'product_id': product_id,
                                'is_read': is_read,
                                'created_at': created_at
                            })
                            
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            error_ids.append(record_id)
                            print(f"    ❌ Error migrating record {record_id}: {e}")
                    
                    conn.commit()
                    print(f"  Progress: {min(offset + self.batch_size, total)}/{total} ({success_count} success, {error_count} errors)")
                    
                    offset += self.batch_size
                    time.sleep(0.1)  # Pause between batches
                    
                except Exception as e:
                    print(f"  ❌ Batch error at offset {offset}: {e}")
                    conn.rollback()
                    offset += self.batch_size
            
            print(f"  ✅ Migration complete: {success_count} success, {error_count} errors")
            return {'success': success_count, 'errors': error_count, 'error_ids': error_ids}
    
    def migrate_rider_chat_messages(self):
        """Migrate RiderChatMessage to ChatMessage"""
        print("\n📦 Migrating RiderChatMessage records...")
        
        with self.engine.connect() as conn:
            # Get total count
            result = conn.execute(text("SELECT COUNT(*) FROM rider_chat_message"))
            total = result.scalar()
            print(f"  Total records to migrate: {total}")
            
            if total == 0:
                print("  ✅ No records to migrate")
                return {'success': 0, 'errors': 0, 'error_ids': []}
            
            success_count = 0
            error_count = 0
            error_ids = []
            
            # Process in batches
            offset = 0
            while offset < total:
                try:
                    # Read batch
                    result = conn.execute(text(f"""
                        SELECT id, buyer_id, rider_id, sender_role, message, order_id, is_read, created_at
                        FROM rider_chat_message
                        ORDER BY id
                        LIMIT {self.batch_size} OFFSET {offset}
                    """))
                    
                    batch = result.fetchall()
                    if not batch:
                        break
                    
                    # Transform and insert
                    for row in batch:
                        try:
                            record_id, buyer_id, rider_id, sender_role, message, order_id, is_read, created_at = row
                            
                            # Determine sender and receiver
                            if sender_role == 'buyer':
                                sender_id = buyer_id
                                receiver_id = rider_id
                            else:  # rider
                                sender_id = rider_id
                                receiver_id = buyer_id
                            
                            # Insert into ChatMessage
                            conn.execute(text("""
                                INSERT INTO chat_message (sender_id, receiver_id, message, product_id, order_id, is_read, created_at)
                                VALUES (:sender_id, :receiver_id, :message, NULL, :order_id, :is_read, :created_at)
                            """), {
                                'sender_id': sender_id,
                                'receiver_id': receiver_id,
                                'message': message,
                                'order_id': order_id,
                                'is_read': is_read,
                                'created_at': created_at
                            })
                            
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            error_ids.append(record_id)
                            print(f"    ❌ Error migrating record {record_id}: {e}")
                    
                    conn.commit()
                    print(f"  Progress: {min(offset + self.batch_size, total)}/{total} ({success_count} success, {error_count} errors)")
                    
                    offset += self.batch_size
                    time.sleep(0.1)  # Pause between batches
                    
                except Exception as e:
                    print(f"  ❌ Batch error at offset {offset}: {e}")
                    conn.rollback()
                    offset += self.batch_size
            
            print(f"  ✅ Migration complete: {success_count} success, {error_count} errors")
            return {'success': success_count, 'errors': error_count, 'error_ids': error_ids}


class DataIntegrityValidator:
    """Validates data integrity after migration"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def validate(self):
        """Run all validation checks"""
        print("\n🔍 Validating data integrity...")
        
        with self.engine.connect() as conn:
            # Count records
            result = conn.execute(text("SELECT COUNT(*) FROM store_chat_message"))
            store_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM rider_chat_message"))
            rider_count = result.scalar()
            
            result = conn.execute(text("SELECT COUNT(*) FROM chat_message"))
            unified_count = result.scalar()
            
            legacy_total = store_count + rider_count
            
            print(f"  Legacy tables total: {legacy_total} ({store_count} store + {rider_count} rider)")
            print(f"  Unified table total: {unified_count}")
            
            if unified_count >= legacy_total:
                print(f"  ✅ Record count validation PASSED")
                return True
            else:
                print(f"  ❌ Record count validation FAILED (missing {legacy_total - unified_count} records)")
                return False


def run_migration():
    """Execute full migration workflow"""
    print("=" * 70)
    print("UNIFIED CHAT SYSTEM MIGRATION")
    print("=" * 70)
    
    try:
        # Connect to database
        db_url = get_db_url()
        engine = create_engine(db_url)
        
        # Check if chat_message table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'chat_message' not in tables:
            print("\n❌ ERROR: chat_message table does not exist!")
            print("Please run migrate_chat_standalone.py first to create the table.")
            return False
        
        # Initialize services
        migration_service = MigrationService(engine)
        validator = DataIntegrityValidator(engine)
        
        # Step 1: Create backups
        backups = migration_service.create_backups()
        
        # Step 2: Migrate StoreChatMessage
        store_result = migration_service.migrate_store_chat_messages()
        
        # Step 3: Migrate RiderChatMessage
        rider_result = migration_service.migrate_rider_chat_messages()
        
        # Step 4: Validate
        validation_passed = validator.validate()
        
        # Summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"StoreChatMessage: {store_result['success']} migrated, {store_result['errors']} errors")
        print(f"RiderChatMessage: {rider_result['success']} migrated, {rider_result['errors']} errors")
        print(f"Validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        print(f"Backups: {len(backups)} files created")
        
        if validation_passed:
            print("\n✅ MIGRATION SUCCESSFUL!")
            print("\n📋 Next steps:")
            print("1. Remove legacy chat routes from app.py (lines 7695-8010)")
            print("2. Test the unified chat API endpoints")
            print("3. Monitor for 48 hours before removing legacy tables")
            return True
        else:
            print("\n❌ MIGRATION FAILED - Validation errors detected")
            print("Please review the errors and consider rollback if needed")
            return False
            
    except Exception as e:
        print(f"\n❌ MIGRATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
