import mysql.connector
from mysql.connector import Error

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kids_ecommerce'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("ALL USERS IN DATABASE")
    print("=" * 80)
    
    cursor.execute("SELECT id, email, role, status, first_name, last_name FROM user ORDER BY id DESC LIMIT 20")
    users = cursor.fetchall()
    
    for user in users:
        uid, email, role, status, fname, lname = user
        print(f"ID: {uid:3} | Email: {email:30} | Role: {role:6} | Status: {status:8} | Name: {fname if fname else ''} {lname if lname else ''}")
    
    # Update the latest pending user to active
    print("\n" + "=" * 80)
    print("UPDATING PENDING USERS TO ACTIVE")
    print("=" * 80)
    
    cursor.execute("SELECT id, email FROM user WHERE status = 'pending' ORDER BY id DESC LIMIT 5")
    pending_users = cursor.fetchall()
    
    for uid, email in pending_users:
        cursor.execute("UPDATE user SET status = 'active' WHERE id = %s", (uid,))
        conn.commit()
        print(f"✓ Updated user {uid} ({email}) to status='active'")
    
    if not pending_users:
        print("No pending users found")
    
    cursor.close()
    conn.close()
    
except Error as e:
    print(f"Error: {e}")
