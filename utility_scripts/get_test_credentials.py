import mysql.connector

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='kids_ecommerce'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Get exact passwords for test accounts
    test_emails = [
        'admin@kidscommerce.com',
        'Matt@gmail.com',
        'rider@gmail.com',
    ]
    
    print('Test account credentials:\n')
    for email in test_emails:
        cursor.execute('SELECT email, role, password FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        if user:
            print(f'{user.get("email")} ({user.get("role")}):')
            print(f'  Password: {user.get("password")}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
