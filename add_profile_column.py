#!/usr/bin/env python3
"""
Add profile_picture column to users table
"""
import psycopg2

# Supabase connection
DB_URL = "postgresql://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

print("=" * 50)
print("ADDING PROFILE_PICTURE COLUMN TO USERS TABLE")
print("=" * 50)

try:
    # Connect
    print("\n1. Connecting to Supabase...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    print("Connected!")
    
    # Add column
    print("\n2. Adding profile_picture column...")
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS profile_picture TEXT;
    """)
    conn.commit()
    print("Column added successfully!")
    
    # Verify
    print("\n3. Verifying column exists...")
    cur.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'profile_picture';
    """)
    result = cur.fetchone()
    
    if result:
        print(f"Column found: {result[0]} ({result[1]}, nullable: {result[2]})")
    else:
        print("Column not found!")
    
    # Check users
    print("\n4. Checking users table...")
    cur.execute("SELECT id, email, role, profile_picture FROM users LIMIT 5")
    users = cur.fetchall()
    
    print(f"\nFound {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, Photo: {user[3]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("SUCCESS! profile_picture column added")
    print("=" * 50)
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
