import mysql.connector
import hashlib

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='kids_ecommerce'
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # Check table structure
    cursor.execute('DESCRIBE user')
    columns = cursor.fetchall()
    print('User table columns:')
    for col in columns:
        print(f'  {col.get("Field")}: {col.get("Type")}')
    
    print('\n' + '='*50 + '\n')
    
    # Get a buyer account with all fields
    cursor.execute('SELECT * FROM user WHERE role = "buyer" LIMIT 1')
    buyer = cursor.fetchone()
    
    if buyer:
        print(f'Sample buyer account: {buyer.get("email")}')
        for key, value in buyer.items():
            if key == 'password':
                print(f'  {key}: {str(value)[:50]}...' if value else 'NULL')
            else:
                print(f'  {key}: {value}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
