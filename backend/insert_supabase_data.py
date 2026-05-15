#!/usr/bin/env python3
"""
Script to insert all data from supabase_data_inserts.sql into Supabase PostgreSQL database
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables - navigate from backend to mobile_app folder
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase.env')
load_dotenv(env_path)

# Database connection details from supabase.env
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'db.ykgwqdboucsiaedgtivx.supabase.co')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')

def insert_data():
    # Read SQL file using base_dir defined at module level
    sql_file_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase_data_inserts.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found at {sql_file_path}")
        return False
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"Loaded SQL file: {len(sql_content)} characters")
    print(f"SQL statements found: {sql_content.count('INSERT INTO')}")
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='require'
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print(f"Connected to database: {DB_HOST}")
        
        # Execute entire SQL content as a single transaction
        # This handles semicolons inside string values correctly
        print("Executing SQL statements...")
        
        try:
            cursor.execute(sql_content)
            success_count = sql_content.count('INSERT INTO')
            error_count = 0
            print(f"  Executed all statements successfully...")
        except Exception as e:
            # If bulk execution fails, try statement by statement with better parsing
            print(f"  Bulk execution failed: {e}")
            print("  Trying individual statement execution...")
            
            # Rollback the failed transaction
            conn.rollback()
            
            import re
            # Split on semicolons that are not inside quotes
            statements = re.split(r";(?=(?:[^'\"]*['\"][^'\"]*['\"])*[^'\"]*$)", sql_content)
            
            success_count = 0
            error_count = 0
            
            for i, statement in enumerate(statements):
                stmt = statement.strip()
                if not stmt or stmt.startswith('--') or stmt == '':
                    continue
                    
                try:
                    cursor.execute(stmt + ';')
                    success_count += 1
                    if success_count % 50 == 0:
                        print(f"  Executed {success_count} statements...")
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Only show first 5 errors
                        print(f"  Error on statement {i}: {str(e)[:100]}")
                    elif error_count == 6:
                        print("  ... (more errors hidden)")
                    # Rollback this failed statement and continue
                    conn.rollback()
                    continue
        
        # Commit all successful statements
        conn.commit()
        print(f"\n{'='*60}")
        print(f"Data insertion complete!")
        print(f"  Successful: {success_count} statements")
        print(f"  Errors: {error_count} statements")
        print(f"{'='*60}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("SUPABASE DATA INSERTION SCRIPT")
    print("="*60)
    print(f"Database Host: {DB_HOST}")
    print(f"Database Name: {DB_NAME}")
    print(f"SQL File: {os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase_data_inserts.sql')}")
    print("="*60)
    print()
    
    # Auto-confirm for automated execution
    print("Starting data insertion...")
    insert_data()
