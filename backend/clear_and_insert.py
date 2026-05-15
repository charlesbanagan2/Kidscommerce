#!/usr/bin/env python3
"""
Clear all data and insert new data from supabase_data_inserts.sql
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

def clear_database(cursor):
    """Clear all tables that exist"""
    cursor.execute("SET session_replication_role = 'replica';")
    
    # Get list of actual tables in database
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%' 
        AND tablename NOT LIKE 'sql_%'
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if not existing_tables:
        print("No tables found to clear.")
        return
    
    # Quote reserved keywords
    reserved = ['order', 'user']
    quoted_tables = [f'"{t}"' if t in reserved else t for t in existing_tables]
    
    cursor.execute(f"TRUNCATE TABLE {', '.join(quoted_tables)} RESTART IDENTITY CASCADE;")
    cursor.execute("SET session_replication_role = 'origin';")
    print(f"Cleared {len(existing_tables)} tables!")

def insert_data(conn, cursor, sql_content):
    """Insert data from SQL file"""
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
            conn.commit()  # Commit each statement individually
            success_count += 1
            if success_count % 50 == 0:
                print(f"  Inserted {success_count} statements...")
        except Exception as e:
            error_count += 1
            if error_count <= 10:
                print(f"  Error on stmt {i}: {str(e)[:80]}")
            conn.rollback()  # Rollback failed statement and continue
            continue
    
    return success_count, error_count

def main():
    print("="*60)
    print("CLEAR AND INSERT DATA")
    print("="*60)
    
    # Read SQL file
    sql_file_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase_data_inserts.sql')
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"Loaded SQL: {len(sql_content)} chars, {sql_content.count('INSERT INTO')} INSERT statements")
    
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = False
    cursor = conn.cursor()
    
    print(f"Connected to {DB_HOST}")
    
    # Step 1: Clear database
    print("\nStep 1: Clearing database...")
    clear_database(cursor)
    conn.commit()
    
    # Step 2: Insert data
    print("\nStep 2: Inserting data...")
    success, errors = insert_data(cursor, sql_content)
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"  Successful: {success} statements")
    print(f"  Errors: {errors} statements")
    print(f"{'='*60}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
