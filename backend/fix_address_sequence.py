"""
Fix address table sequence issue
Run this script to reset the address ID sequence
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

if not SUPABASE_DB_URL:
    print("❌ Error: SUPABASE_DB_URL not found in environment variables")
    sys.exit(1)

print("🔧 Fixing address table sequence...")
print(f"📊 Database: {SUPABASE_DB_URL.split('@')[1].split('/')[0]}")

try:
    # Create database connection
    engine = create_engine(SUPABASE_DB_URL)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Get current max ID
            result = conn.execute(text("SELECT COALESCE(MAX(id), 0) as max_id FROM address"))
            max_id = result.fetchone()[0]
            print(f"📈 Current max ID in address table: {max_id}")
            
            # Reset sequence to max_id (setval with true means "is_called")
            # This will make the next value be max_id + 1
            conn.execute(text(f"SELECT setval('address_id_seq', {max_id}, true)"))
            print(f"✅ Sequence set to: {max_id} (next will be {max_id + 1})")
            
            # Verify the fix
            result = conn.execute(text("SELECT nextval('address_id_seq') as next_val"))
            next_val = result.fetchone()[0]
            print(f"✅ Next address ID will be: {next_val}")
            
            # Reset back so we don't skip a number
            conn.execute(text(f"SELECT setval('address_id_seq', {max_id}, true)"))
            
            # Commit transaction
            trans.commit()
            print("\n✅ Address sequence fixed successfully!")
            print(f"   Next address ID will be: {max_id + 1}")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error during fix: {e}")
            raise
            
except Exception as e:
    print(f"\n❌ Database connection error: {e}")
    sys.exit(1)

print("\n🎉 Done! You can now register users with addresses.")
