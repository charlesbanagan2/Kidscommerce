#!/usr/bin/env python3
"""
Add missing columns to match the SQL file schema
"""

import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase.env')
load_dotenv(env_path)

DB_HOST = 'db.ykgwqdboucsiaedgtivx.supabase.co'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')
DB_PORT = '5432'

def update_schema():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Updating database schema...")
    
    # Add missing columns
    alter_statements = [
        # user table
        'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS username VARCHAR(80);',
        
        # seller_application table  
        'ALTER TABLE seller_application ADD COLUMN IF NOT EXISTS business_name VARCHAR(255);',
        
        # order table
        'ALTER TABLE "order" ADD COLUMN IF NOT EXISTS stock_deducted_at TIMESTAMP;',
        
        # notification table
        'ALTER TABLE notification ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;',
        
        # return_request table
        'ALTER TABLE return_request ADD COLUMN IF NOT EXISTS shipping_instruction TEXT;',
        
        # admin_security_log table
        'ALTER TABLE admin_security_log ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;',
    ]
    
    for stmt in alter_statements:
        try:
            cursor.execute(stmt)
            print(f"  [OK] {stmt[:60]}...")
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
    
    print("\nSchema update complete!")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    update_schema()
