import mysql.connector
from werkzeug.security import generate_password_hash
import bcrypt

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
    print("CREATING TEST USER FOR CART TESTING")
    print("=" * 80)
    
    # Create a test buyer with properly hashed password using bcrypt
    email = "test_cart_buyer@example.com"
    password = "Test@1234"
    first_name = "Cart"
    last_name = "Test"
    
    # Use bcrypt to hash the password (what the backend expects)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"\nEmail: {email}")
    print(f"Password: {password}")
    print(f"Hashed (bcrypt): {hashed_password[:50]}...")
    
    # Check if user already exists
    cursor.execute("SELECT id, email FROM user WHERE email = %s", (email,))
    existing = cursor.fetchone()
    
    if existing:
        uid = existing[0]
        # Update existing user
        cursor.execute(
            "UPDATE user SET password = %s, status = 'active', role = 'buyer', first_name = %s, last_name = %s WHERE id = %s",
            (hashed_password, first_name, last_name, uid)
        )
        print(f"\n✓ Updated existing user (ID: {uid})")
    else:
        # Insert new user
        cursor.execute(
            "INSERT INTO user (email, password, first_name, last_name, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (email, hashed_password, first_name, last_name, 'buyer', 'active')
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"\n✓ Created new user (ID: {new_id})")
    
    conn.commit()
    
    print(f"\n✓ User credentials saved to database")
    print(f"\nYou can now login with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
