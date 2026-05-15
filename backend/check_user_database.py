import psycopg2

try:
    # Connect to Supabase PostgreSQL
    conn = psycopg2.connect(
        host="db.ykgwqdboucsiaedgtivx.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="Kidscommerce@1234"
    )
    
    cursor = conn.cursor()
    
    # Query for the user
    cursor.execute("""
        SELECT id, email, password, role, status 
        FROM "user" 
        WHERE email = %s
    """, ('juanrider@gmail.com',))
    
    result = cursor.fetchone()
    
    if result:
        print("✓ User found in Supabase!")
        print(f"ID: {result[0]}")
        print(f"Email: {result[1]}")
        print(f"Password: {result[2]}")
        print(f"Role: {result[3]}")
        print(f"Status: {result[4]}")
        print(f"\nPassword starts with $2b$: {result[2].startswith('$2b$') if result[2] else False}")
    else:
        print("✗ User NOT found in Supabase database!")
        print("The user exists in local SQLite but not in Supabase.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    print("\nTrying to check if user exists in local SQLite instead...")
    
    import sqlite3
    conn = sqlite3.connect('instance/kids_ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, password, role, status FROM user WHERE email = ?', ('juanrider@gmail.com',))
    result = cursor.fetchone()
    
    if result:
        print("\nUser found in LOCAL SQLite database:")
        print(f"ID: {result[0]}")
        print(f"Email: {result[1]}")
        print(f"Password: {result[2]}")
        print(f"Role: {result[3]}")
        print(f"Status: {result[4]}")
        print(f"\nISSUE: Your mobile app is trying to login via API which uses Supabase,")
        print("but the user only exists in the local SQLite database!")
    
    conn.close()
