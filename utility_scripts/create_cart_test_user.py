import mysql.connector
import bcrypt

# Create a test user with bcrypt-hashed password
password = 'Test@12345'
salt = bcrypt.gensalt(rounds=12)
password_hash = bcrypt.hashpw(password.encode(), salt).decode()

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='kids_ecommerce'
)
cursor = conn.cursor()

# Delete the old test user if it exists
cursor.execute('DELETE FROM user WHERE email = %s', ('carttest123@example.com',))

# Insert a test buyer with bcrypt hash
email = 'carttest123@example.com'
cursor.execute(
    """INSERT INTO user (first_name, last_name, email, phone, password, role, status, address)
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
    ('Cart', 'Test', email, '09987654321', password_hash, 'buyer', 'active', '123 Test St')
)
conn.commit()
print(f'User created with email: {email}')
print(f'Password: {password}')
print(f'Hash format: bcrypt')

cursor.close()
conn.close()
