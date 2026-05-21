"""
Add missing columns to address table
Run this script to fix the address table structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

def add_address_columns():
    """Add missing columns to address table"""
    
    sql_commands = [
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS street_address TEXT;
        """,
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS city TEXT;
        """,
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS province TEXT;
        """,
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS region TEXT;
        """,
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS barangay TEXT;
        """,
        """
        ALTER TABLE address 
        ADD COLUMN IF NOT EXISTS zip_code TEXT;
        """
    ]
    
    print("Adding missing columns to address table...")
    
    for sql in sql_commands:
        try:
            result = supabase.rpc('exec_sql', {'query': sql}).execute()
            print(f"✓ Executed: {sql.strip()[:50]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"  SQL: {sql.strip()[:50]}...")
    
    print("\n✓ Migration completed!")
    print("\nVerifying address table structure...")
    
    # Try to fetch one address to see the structure
    try:
        result = supabase.table('address').select('*').limit(1).execute()
        if result.data:
            print(f"\nAddress table columns: {list(result.data[0].keys())}")
        else:
            print("\nNo addresses in table yet")
    except Exception as e:
        print(f"\nCouldn't verify: {e}")

if __name__ == '__main__':
    add_address_columns()
