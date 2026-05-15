import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kids_ecommerce'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Get the test user
cursor.execute("SELECT id, email, password, status, role FROM user WHERE email = %s", ("test_cart_buyer@example.com",))
user = cursor.fetchone()

if user:
    uid, email, password_hash, status, role = user
    print("User found in database:")
    print(f"  ID: {uid}")
    print(f"  Email: {email}")
    print(f"  Password Hash: {password_hash[:60]}...")
    print(f"  Status: {status}")
    print(f"  Role: {role}")
    
    # Test password verification
    from werkzeug.security import check_password_hash
    test_password = "Test@1234"
    
    is_valid = check_password_hash(password_hash, test_password)
    print(f"\nPassword verification:")
    print(f"  Test password: {test_password}")
    print(f"  Valid: {is_valid}")
else:
    print("User not found!")

cursor.close()
conn.close()
