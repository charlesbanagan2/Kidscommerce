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
    
    # Find accounts with non-google passwords
    cursor.execute("""
        SELECT id, email, role, status, password 
        FROM user 
        WHERE password NOT LIKE '%google%' AND password NOT LIKE '%facebook%' 
        AND password IS NOT NULL
        LIMIT 10
    """)
    users = cursor.fetchall()
    
    print(f'Found {len(users)} accounts with potential passwords:\n')
    for user in users:
        pwd_preview = str(user.get("password"))[:30] if user.get("password") else "NULL"
        print(f'  {user.get("email")} ({user.get("role")})')
        print(f'    Password: {pwd_preview}...')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
