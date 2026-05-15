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
    cursor.execute('SELECT * FROM user WHERE email = %s', ('charliebanagan33@gmail.com',))
    user = cursor.fetchone()
    
    if user:
        print('✅ User found!')
        print(f'ID: {user.get("id")}')
        print(f'Name: {user.get("first_name")} {user.get("last_name")}')
        print(f'Email: {user.get("email")}')
        print(f'Role: {user.get("role")}')
        print(f'Status: {user.get("status")}')
        print(f'Phone: {user.get("phone")}')
    else:
        print('❌ User NOT found in database')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
