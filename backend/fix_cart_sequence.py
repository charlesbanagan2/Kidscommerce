"""
Fix Cart Table Sequence - Run this to fix the duplicate key error
"""
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Get database connection string
db_url = os.getenv('SUPABASE_DB_URL')

if not db_url:
    print("❌ SUPABASE_DB_URL not found in .env file")
    exit(1)

try:
    # Connect to database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print("🔍 Checking cart table...")
    
    # Get current max ID
    cursor.execute("SELECT MAX(id) FROM cart;")
    max_id = cursor.fetchone()[0]
    
    if max_id is None:
        max_id = 0
        print(f"   Cart table is empty, will start from ID 1")
    else:
        print(f"   Highest cart ID: {max_id}")
    
    # Get current sequence value
    cursor.execute("SELECT last_value FROM cart_id_seq;")
    seq_value = cursor.fetchone()[0]
    print(f"   Current sequence value: {seq_value}")
    
    # Fix the sequence
    new_seq_value = max_id + 1
    cursor.execute(f"SELECT setval('cart_id_seq', {new_seq_value}, false);")
    
    # Commit changes
    conn.commit()
    
    print(f"\n✅ Fixed! Next cart ID will be: {new_seq_value}")
    print("   You can now add items to cart without errors.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nAlternative: Run this SQL in Supabase SQL Editor:")
    print("SELECT setval('cart_id_seq', COALESCE((SELECT MAX(id) FROM cart), 0) + 1, false);")
