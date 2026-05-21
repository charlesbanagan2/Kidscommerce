#!/usr/bin/env python3
import psycopg2

DB_URL = "postgresql://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

print("Checking database tables...")

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # List all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check for user-related tables
    print("\n\nLooking for user tables...")
    user_tables = [t[0] for t in tables if 'user' in t[0].lower()]
    
    if user_tables:
        print(f"Found user tables: {user_tables}")
        
        for table_name in user_tables:
            print(f"\n\nColumns in {table_name}:")
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check if profile_picture exists
            has_profile_pic = any(col[0] == 'profile_picture' for col in columns)
            
            if not has_profile_pic:
                print(f"\n  Adding profile_picture to {table_name}...")
                cur.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS profile_picture TEXT;")
                conn.commit()
                print(f"  SUCCESS! Added to {table_name}")
    else:
        print("No user tables found!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\nError: {e}")
