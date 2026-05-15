import sqlite3

# Connect to database
conn = sqlite3.connect('instance/kids_ecommerce.db')
cursor = conn.cursor()

# Check current status of juanrider@gmail.com
cursor.execute('SELECT id, email, role, status FROM user WHERE email = ?', ('juanrider@gmail.com',))
user = cursor.fetchone()
print(f"Current user: {user}")

# Update juanrider@gmail.com to active
cursor.execute('UPDATE user SET status = ? WHERE email = ? AND role = ?', ('active', 'juanrider@gmail.com', 'rider'))
print(f"Updated juanrider@gmail.com to active status")

# Update all approved riders to active
cursor.execute('UPDATE user SET status = ? WHERE status = ? AND role = ?', ('active', 'approved', 'rider'))
affected = cursor.rowcount
print(f"Updated {affected} approved riders to active status")

# Commit changes
conn.commit()

# Verify changes
cursor.execute('SELECT id, email, role, status FROM user WHERE email = ?', ('juanrider@gmail.com',))
updated_user = cursor.fetchone()
print(f"Updated user: {updated_user}")

# Show all active riders
cursor.execute('SELECT id, email, role, status FROM user WHERE role = ? AND status = ?', ('rider', 'active'))
active_riders = cursor.fetchall()
print(f"\nAll active riders ({len(active_riders)}):")
for rider in active_riders:
    print(f"  ID: {rider[0]}, Email: {rider[1]}, Role: {rider[2]}, Status: {rider[3]}")

conn.close()
print("\nDatabase updated successfully!")
