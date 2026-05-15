import sqlite3

# Add profile_picture column to users table
conn = sqlite3.connect('instance/kids_ecommerce.db')
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'profile_picture' not in columns:
        cursor.execute("ALTER TABLE user ADD COLUMN profile_picture VARCHAR(255)")
        conn.commit()
        print("[OK] Added profile_picture column to user table")
    else:
        print("[OK] profile_picture column already exists")
        
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close()
