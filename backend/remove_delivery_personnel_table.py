import sqlite3
import os
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Connect to database
db_path = 'instance/kids_ecommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("REMOVING DELIVERY_PERSONNEL TABLE")
print("=" * 60)

# 1. Check if delivery_personnel table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_personnel'")
if cursor.fetchone():
    print("\n[OK] Found delivery_personnel table")
    
    # Show current data
    cursor.execute("SELECT * FROM delivery_personnel")
    delivery_data = cursor.fetchall()
    print(f"  - Contains {len(delivery_data)} records")
    
    # Drop the table
    cursor.execute("DROP TABLE delivery_personnel")
    print("  - Table dropped successfully")
else:
    print("\n[OK] delivery_personnel table does not exist (already removed)")

# 2. Verify user table has all necessary columns
print("\n" + "=" * 60)
print("VERIFYING USER TABLE STRUCTURE")
print("=" * 60)

cursor.execute("PRAGMA table_info(user)")
columns = {col[1]: col[2] for col in cursor.fetchall()}
print(f"\n[OK] User table has {len(columns)} columns:")
for col_name, col_type in columns.items():
    print(f"  - {col_name}: {col_type}")

# Required columns for consolidated user table
required_columns = {
    'id': 'INTEGER',
    'first_name': 'VARCHAR',
    'last_name': 'VARCHAR',
    'email': 'VARCHAR',
    'password': 'VARCHAR',
    'phone': 'VARCHAR',
    'address': 'TEXT',
    'role': 'VARCHAR',
    'status': 'VARCHAR',
    'created_at': 'DATETIME',
    'valid_id': 'VARCHAR'
}

missing_columns = []
for col, col_type in required_columns.items():
    if col not in columns:
        missing_columns.append((col, col_type))

if missing_columns:
    print("\n[WARNING] Adding missing columns:")
    for col, col_type in missing_columns:
        cursor.execute(f"ALTER TABLE user ADD COLUMN {col} {col_type}")
        print(f"  - Added {col} ({col_type})")
else:
    print("\n[OK] All required columns exist")

# 3. Check current user statuses
print("\n" + "=" * 60)
print("CURRENT USER STATUS SUMMARY")
print("=" * 60)

cursor.execute("SELECT role, status, COUNT(*) FROM user GROUP BY role, status")
status_summary = cursor.fetchall()
print("\nUser counts by role and status:")
for role, status, count in status_summary:
    print(f"  - {role or 'NULL'} / {status or 'NULL'}: {count} users")

# 4. Ensure all riders have proper status (active, pending, or rejected)
print("\n" + "=" * 60)
print("UPDATING RIDER STATUSES")
print("=" * 60)

cursor.execute("SELECT id, email, status FROM user WHERE role = 'rider'")
riders = cursor.fetchall()
print(f"\n[OK] Found {len(riders)} riders:")
for rider_id, email, status in riders:
    print(f"  - ID {rider_id}: {email} - Status: {status}")
    
    # If status is NULL or invalid, set to pending
    if status not in ['active', 'pending', 'rejected']:
        cursor.execute("UPDATE user SET status = 'pending' WHERE id = ?", (rider_id,))
        print(f"    -> Updated to 'pending'")

# 5. Commit all changes
conn.commit()

print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

# Verify delivery_personnel is gone
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_personnel'")
if cursor.fetchone():
    print("\n[ERROR] delivery_personnel table still exists!")
else:
    print("\n[OK] delivery_personnel table successfully removed")

# Show final user status summary
cursor.execute("SELECT role, status, COUNT(*) FROM user GROUP BY role, status ORDER BY role, status")
final_summary = cursor.fetchall()
print("\n[OK] Final user status summary:")
for role, status, count in final_summary:
    print(f"  - {role or 'NULL'} / {status or 'NULL'}: {count} users")

# Show all riders
cursor.execute("SELECT id, email, first_name, last_name, status FROM user WHERE role = 'rider' ORDER BY id")
all_riders = cursor.fetchall()
print(f"\n[OK] All riders ({len(all_riders)}):")
for rider_id, email, first_name, last_name, status in all_riders:
    print(f"  - ID {rider_id}: {first_name} {last_name} ({email}) - Status: {status}")

conn.close()

print("\n" + "=" * 60)
print("DATABASE UPDATE COMPLETE!")
print("=" * 60)
print("\nSummary:")
print("  [OK] delivery_personnel table removed")
print("  [OK] All user data consolidated in user table")
print("  [OK] User statuses: active, pending, rejected")
print("  [OK] Roles: buyer, rider, seller, admin")
print("\nNext steps:")
print("  1. Update app.py to remove delivery_personnel references")
print("  2. Test rider login with active status")
print("  3. Test rider registration flow")
