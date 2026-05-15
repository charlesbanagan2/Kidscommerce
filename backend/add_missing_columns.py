#!/usr/bin/env python3
"""
Add missing columns to the order table
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

def add_missing_columns():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Checking order table for missing columns...")
    
    # Check if return_reason column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'order' 
        AND column_name = 'return_reason'
    """)
    has_return_reason = cursor.fetchone()
    
    if not has_return_reason:
        print("Adding 'return_reason' column...")
        cursor.execute('ALTER TABLE "order" ADD COLUMN return_reason TEXT;')
        print("  Done!")
    else:
        print("  'return_reason' column already exists")
    
    cursor.close()
    conn.close()
    print("\nFix complete!")

if __name__ == '__main__':
    add_missing_columns()
