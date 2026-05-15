#!/usr/bin/env python3
"""
Reorder SQL INSERT statements by dependency order and insert into database
"""

import os
import re
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

# Table dependency order (parent tables first)
TABLE_ORDER = [
    # Independent tables first
    'user',
    'category',
    'subcategory',
    'hero_slide',
    'coupon',
    
    # Tables that depend on user
    'admin_profile',
    'seller_application',
    'rider_application',
    'delivery_personnel',
    'flask_dance_oauth',
    'address',
    'notification_preferences',
    'password_reset_token',
    'follow',
    
    # Product-related
    'product',
    
    # Order-related (depends on user and product)
    'order',
    'order_item',
    'cart',
    'wishlist',
    
    # Reviews and notifications
    'product_review',
    'notification',
    
    # Logs and messages
    'admin_security_log',
    'conversation',
    'chat_participant',
    'chat_message',
    
    # Returns
    'return_request',
    
    # Wallet
    'wallet_transaction',
]

def parse_sql_file(filepath):
    """Parse SQL file and extract INSERT statements by table"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all INSERT statements
    insert_pattern = r'INSERT INTO "([^"]+)" \([^)]+\) VALUES[\s\S]*?;'
    matches = list(re.finditer(insert_pattern, content))
    
    statements_by_table = {}
    for match in matches:
        table_name = match.group(1)
        statement = match.group(0)
        
        if table_name not in statements_by_table:
            statements_by_table[table_name] = []
        statements_by_table[table_name].append(statement)
    
    return statements_by_table

def clear_database(cursor):
    """Clear all tables"""
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%' 
        AND tablename NOT LIKE 'sql_%'
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if not existing_tables:
        return
    
    # Quote reserved keywords
    reserved = ['order', 'user']
    quoted_tables = [f'"{t}"' if t in reserved else t for t in existing_tables]
    
    cursor.execute("SET session_replication_role = 'replica';")
    cursor.execute(f"TRUNCATE TABLE {', '.join(quoted_tables)} RESTART IDENTITY CASCADE;")
    cursor.execute("SET session_replication_role = 'origin';")
    print(f"Cleared {len(existing_tables)} tables!")

def insert_statements(conn, cursor, statements_by_table):
    """Insert statements in dependency order"""
    total_success = 0
    total_errors = 0
    
    for table in TABLE_ORDER:
        if table not in statements_by_table:
            continue
        
        statements = statements_by_table[table]
        print(f"\n  Inserting into '{table}' ({len(statements)} statements)...")
        
        table_success = 0
        table_errors = 0
        
        for stmt in statements:
            try:
                cursor.execute(stmt)
                conn.commit()
                table_success += 1
                total_success += 1
            except Exception as e:
                table_errors += 1
                total_errors += 1
                conn.rollback()
                if table_errors <= 3:
                    error_msg = str(e)[:80]
                    # Check for schema mismatch
                    if 'does not exist' in error_msg:
                        print(f"    SCHEMA MISMATCH: {error_msg}")
                        print(f"    Skipping remaining statements for this table...")
                        break
                    else:
                        print(f"    Error: {error_msg}")
        
        print(f"    [OK] {table_success} success, {table_errors} errors")
    
    return total_success, total_errors

def main():
    print("="*60)
    print("REORDER AND INSERT SQL DATA")
    print("="*60)
    
    # Read SQL file
    sql_file_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase_data_inserts.sql')
    print(f"Parsing {sql_file_path}...")
    
    statements_by_table = parse_sql_file(sql_file_path)
    print(f"Found {len(statements_by_table)} tables with INSERT statements")
    
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
    
    # Step 2: Insert in dependency order
    print("\nStep 2: Inserting data in dependency order...")
    success, errors = insert_statements(conn, cursor, statements_by_table)
    
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"  Total Successful: {success} statements")
    print(f"  Total Errors: {errors} statements")
    print(f"{'='*60}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
