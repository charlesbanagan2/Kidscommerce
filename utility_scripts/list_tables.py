import mysql.connector

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='kids_ecommerce'
    )
    
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    print('Tables in kids_ecommerce database:')
    for table in tables:
        print(f'  - {table[0]}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
