#!/usr/bin/env python3
"""
Verify order table columns in detail
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

def verify_columns():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Listing all columns in 'order' table:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'order'
        ORDER BY ordinal_position
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]:30} {row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    verify_columns()
