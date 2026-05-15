import mysql.connector
from werkzeug.security import check_password_hash

conn = mysql.connector.connect(host='127.0.0.1', user='root', password='', database='kids_ecommerce')
cursor = conn.cursor()

# Get the user we just created
cursor.execute('SELECT password FROM user WHERE email = %s', ('carttest123@example.com',))
result = cursor.fetchone()

if result:
    stored_hash = result[0]
    print(f'Stored hash: {stored_hash[:50]}...')
    
    # Test if password verification works
    test_password = 'Test@12345'
    is_valid = check_password_hash(stored_hash, test_password)
    print(f'Password Test@12345 is valid: {is_valid}')
else:
    print('User not found')

cursor.close()
conn.close()
