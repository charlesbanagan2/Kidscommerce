"""
Add user from local SQLite to Supabase database
"""
import psycopg2
import sqlite3
from datetime import datetime

# Get user from local SQLite
sqlite_conn = sqlite3.connect('instance/kids_ecommerce.db')
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute('SELECT * FROM user WHERE email = ?', ('juanrider@gmail.com',))
columns = [description[0] for description in sqlite_cursor.description]
user_data = sqlite_cursor.fetchone()

if not user_data:
    print("User not found in local database!")
    exit(1)

user = dict(zip(columns, user_data))
print(f"Found user in local database: {user['email']}")
print(f"Role: {user['role']}, Status: {user['status']}")

sqlite_conn.close()

# Connect to Supabase PostgreSQL
try:
    pg_conn = psycopg2.connect(
        host="db.ykgwqdboucsiaedgtivx.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="Kidscommerce@1234"
    )
    
    pg_cursor = pg_conn.cursor()
    
    # Check if user already exists
    pg_cursor.execute('SELECT id FROM "user" WHERE email = %s', (user['email'],))
    existing = pg_cursor.fetchone()
    
    if existing:
        print(f"\nUser already exists in Supabase with ID: {existing[0]}")
        print("Updating user data...")
        
        pg_cursor.execute("""
            UPDATE "user" 
            SET password = %s, role = %s, status = %s, phone = %s, 
                first_name = %s, last_name = %s, updated_at = %s
            WHERE email = %s
        """, (
            user['password'],
            user['role'],
            user['status'],
            user.get('phone'),
            user.get('first_name'),
            user.get('last_name'),
            datetime.now(),
            user['email']
        ))
    else:
        print("\nInserting user into Supabase...")
        
        pg_cursor.execute("""
            INSERT INTO "user" (email, password, role, status, phone, first_name, last_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user['email'],
            user['password'],
            user['role'],
            user['status'],
            user.get('phone'),
            user.get('first_name'),
            user.get('last_name'),
            user.get('created_at', datetime.now()),
            datetime.now()
        ))
        
        new_id = pg_cursor.fetchone()[0]
        print(f"User created in Supabase with ID: {new_id}")
    
    pg_conn.commit()
    print("\nSUCCESS! User is now in Supabase database.")
    print(f"You can now login with: {user['email']} / {user['password']}")
    
    pg_cursor.close()
    pg_conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\nERROR: Cannot connect to Supabase: {e}")
    print("\nPossible reasons:")
    print("1. No internet connection")
    print("2. Supabase credentials are incorrect")
    print("3. Firewall blocking the connection")
    print("\nAlternative: Use local database mode by setting USE_LOCAL_ORM_FALLBACK=True in app.py")
except Exception as e:
    print(f"\nERROR: {e}")
