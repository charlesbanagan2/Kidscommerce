#!/usr/bin/env python3
"""
Add missing created_at column to admin_security_log table
"""

import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase.env')
load_dotenv(env_path)

DB_HOST = os.getenv('SUPABASE_DB_HOST')
DB_NAME = os.getenv('SUPABASE_DB_NAME')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')

def fix_table():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Checking admin_security_log table structure...")
    
    # Check if timestamp column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'admin_security_log' 
        AND column_name = 'timestamp'
    """)
    has_timestamp = cursor.fetchone()
    
    # Check if created_at column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'admin_security_log' 
        AND column_name = 'created_at'
    """)
    has_created_at = cursor.fetchone()
    
    print(f"  Has 'timestamp' column: {has_timestamp is not None}")
    print(f"  Has 'created_at' column: {has_created_at is not None}")
    
    if has_timestamp and not has_created_at:
        print("\nRenaming 'timestamp' to 'created_at'...")
        cursor.execute('ALTER TABLE admin_security_log RENAME COLUMN timestamp TO created_at;')
        print("  Done!")
    elif not has_timestamp and not has_created_at:
        print("\nAdding 'created_at' column...")
        cursor.execute('ALTER TABLE admin_security_log ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();')
        print("  Done!")
    elif has_timestamp and has_created_at:
        print("\nDropping 'timestamp' column (keeping 'created_at')...")
        cursor.execute('ALTER TABLE admin_security_log DROP COLUMN timestamp;')
        print("  Done!")
    else:
        print("\nTable already has correct schema!")
    
    cursor.close()
    conn.close()
    print("\nFix complete!")

if __name__ == '__main__':
    fix_table()
