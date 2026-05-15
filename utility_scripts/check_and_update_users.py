import sqlite3
import sys

# Try to connect to the database
db_paths = [
    'c:\\Users\\mnban\\Documents\\kids\\kids_ecommerce.db',
    'c:\\Users\\mnban\\Documents\\kids\\backend\\kids_ecommerce.db',
    'c:\\Users\\mnban\\Documents\\kids\\backend\\instance\\kids_ecommerce.db'
]

db_path = None
for path in db_paths:
    try:
        conn = sqlite3.connect(path)
        conn.execute("SELECT 1")
        db_path = path
        print(f"✓ Connected to: {path}")
        break
    except:
        pass

if not db_path:
    print("✗ Could not find database")
    sys.exit(1)

# List all users
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "=" * 80)
print("ALL USERS IN DATABASE")
print("=" * 80)

cursor.execute("SELECT id, email, role, status, first_name, last_name FROM user ORDER BY id")
users = cursor.fetchall()

for user in users:
    uid, email, role, status, fname, lname = user
    print(f"ID: {uid:3} | Email: {email:30} | Role: {role:6} | Status: {status:8} | Name: {fname} {lname}")

# Update the most recent user to active status
print("\n" + "=" * 80)
print("UPDATING LATEST USER TO ACTIVE STATUS")
print("=" * 80)

cursor.execute("SELECT id, email FROM user ORDER BY id DESC LIMIT 1")
latest = cursor.fetchone()

if latest:
    uid, email = latest
    cursor.execute("UPDATE user SET status = 'active' WHERE id = ?", (uid,))
    conn.commit()
    print(f"✓ Updated user {uid} ({email}) to status='active'")
else:
    print("No users found")

conn.close()
