import sqlite3

print("=" * 70)
print("VERIFICATION: Database Consolidation")
print("=" * 70)

conn = sqlite3.connect('instance/kids_ecommerce.db')
cursor = conn.cursor()

# 1. Verify delivery_personnel table is gone
print("\n1. Checking if delivery_personnel table exists...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_personnel'")
if cursor.fetchone():
    print("   [ERROR] delivery_personnel table still exists!")
else:
    print("   [OK] delivery_personnel table successfully removed")

# 2. Check user table structure
print("\n2. Verifying user table has required columns...")
cursor.execute("PRAGMA table_info(user)")
columns = {col[1] for col in cursor.fetchall()}
required = ['id', 'email', 'role', 'status', 'phone', 'address']
missing = [c for c in required if c not in columns]
if missing:
    print(f"   [ERROR] Missing columns: {missing}")
else:
    print("   [OK] All required columns present")

# 3. Check rider accounts
print("\n3. Checking rider accounts...")
cursor.execute("SELECT id, email, first_name, last_name, status FROM user WHERE role = 'rider'")
riders = cursor.fetchall()
print(f"   Found {len(riders)} riders:")
for rider_id, email, first_name, last_name, status in riders:
    status_icon = "[OK]" if status == 'active' else "[PENDING]" if status == 'pending' else "[REJECTED]"
    print(f"   {status_icon} ID {rider_id}: {first_name} {last_name} ({email}) - {status}")

# 4. Check juanrider@gmail.com specifically
print("\n4. Verifying juanrider@gmail.com status...")
cursor.execute("SELECT id, status, role FROM user WHERE email = 'juanrider@gmail.com'")
result = cursor.fetchone()
if result:
    user_id, status, role = result
    if status == 'active' and role == 'rider':
        print(f"   [OK] juanrider@gmail.com is active (ID: {user_id})")
    else:
        print(f"   [ERROR] juanrider@gmail.com status: {status}, role: {role}")
else:
    print("   [ERROR] juanrider@gmail.com not found!")

# 5. Check for any 'approved' status users
print("\n5. Checking for users with 'approved' status...")
cursor.execute("SELECT COUNT(*) FROM user WHERE status = 'approved'")
count = cursor.fetchone()[0]
if count == 0:
    print("   [OK] No users with 'approved' status")
else:
    print(f"   [WARNING] Found {count} users with 'approved' status")
    cursor.execute("SELECT id, email, role FROM user WHERE status = 'approved'")
    for user_id, email, role in cursor.fetchall():
        print(f"      - ID {user_id}: {email} ({role})")

# 6. Summary of all user statuses
print("\n6. User status summary:")
cursor.execute("SELECT role, status, COUNT(*) FROM user GROUP BY role, status ORDER BY role, status")
for role, status, count in cursor.fetchall():
    print(f"   {role or 'NULL'} / {status or 'NULL'}: {count} users")

conn.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nRECOMMENDATIONS:")
print("1. Test rider login with juanrider@gmail.com")
print("2. Remove delivery_personnel references from app.py")
print("3. Test rider registration flow")
print("4. Update mobile app if it references delivery_personnel")
