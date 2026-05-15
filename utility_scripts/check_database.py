#!/usr/bin/env python3
"""
Database Check - Find Available Test Accounts
"""

import sqlite3
from pathlib import Path

# Look for the database file
possible_paths = [
    "c:/Users/mnban/Documents/kids/instance/kids_ecommerce.db",
    "c:/Users/mnban/Documents/kids/kids_ecommerce.db",
    "c:/Users/mnban/Documents/kids/mobile_app/kids_ecommerce.db",
]

def find_database():
    """Find the database file"""
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    # Try to find it recursively
    root_dir = Path("c:/Users/mnban/Documents/kids")
    for db_file in root_dir.rglob("*.db"):
        if "kids_ecommerce" in str(db_file) or "app.db" in str(db_file):
            return str(db_file)
    
    return None

def check_database():
    """Check database and find test accounts"""
    db_path = find_database()
    
    if not db_path:
        print("❌ Database file not found!")
        print("Searched in:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    print(f"✅ Found database: {db_path}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("=== DATABASE TABLES ===")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Check users table
        if any('user' in t[0].lower() for t in tables):
            print("=== USERS IN DATABASE ===")
            
            # Try different table names
            user_tables = ['user', 'users', 'buyer', 'buyer_user', 'user_account']
            
            for table_name in user_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"\n{table_name} ({count} records):")
                    
                    # Get columns
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Select relevant columns
                    id_col = 'id' if 'id' in columns else None
                    email_col = next((c for c in columns if 'email' in c.lower()), None)
                    role_col = next((c for c in columns if 'role' in c.lower()), None)
                    
                    if email_col:
                        query = f"SELECT {id_col or 'id'}, {email_col}"
                        if role_col:
                            query += f", {role_col}"
                        query += f" FROM {table_name} LIMIT 10"
                        
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        for row in rows:
                            print(f"  ID: {row[0]}, Email: {row[1]}" + (f", Role: {row[2]}" if len(row) > 2 else ""))
                except sqlite3.OperationalError:
                    pass
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_database()
