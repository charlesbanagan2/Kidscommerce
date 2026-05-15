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
    
    # Check babybliss account
    cursor.execute('SELECT id, email, role, status, password FROM user WHERE email = %s', ('babybliss@gmail.com',))
    user = cursor.fetchone()
    
    if user:
        print('User: babybliss@gmail.com')
        print(f'  Role: {user.get("role")}')
        print(f'  Status: {user.get("status")}')
        print(f'  Password hash exists: {"Yes" if user.get("password") else "No"}')
        if user.get("password"):
            print(f'  Password (first 20 chars): {str(user.get("password"))[:20]}...')
    else:
        print('User not found')
    
    # List some buyer accounts with password info
    print('\nBuyer accounts with password info:')
    cursor.execute('SELECT id, email, role, status, password FROM user WHERE role = "buyer" LIMIT 5')
    buyers = cursor.fetchall()
    for buyer in buyers:
        print(f'  {buyer.get("email")} - Password: {"Yes" if buyer.get("password") else "No"}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
