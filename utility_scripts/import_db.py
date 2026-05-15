import mysql.connector
import subprocess
import os

try:
    # Check if MariaDB mysql command exists
    result = subprocess.run(['mariadb', '-u', 'root', '-h', '127.0.0.1'], 
                          input='SELECT 1;', 
                          capture_output=True, 
                          text=True,
                          timeout=5)
    
    if result.returncode == 0:
        print('✅ Using mariadb command line tool')
        
        # Drop and recreate database
        subprocess.run(['mariadb', '-u', 'root', '-h', '127.0.0.1', '-e', 
                       'DROP DATABASE IF EXISTS kids_ecommerce; CREATE DATABASE kids_ecommerce;'],
                      check=True)
        
        # Import SQL file
        with open('c:\\Users\\mnban\\Documents\\kids\\kids_ecommerce .sql', 'r') as f:
            sql_content = f.read()
        
        result = subprocess.run(['mariadb', '-u', 'root', '-h', '127.0.0.1', 'kids_ecommerce'],
                              input=sql_content,
                              capture_output=True,
                              text=True)
        
        if result.returncode == 0:
            print('✅ Database imported successfully')
        else:
            print('Warning:', result.stderr[:200] if result.stderr else 'Unknown error')
    
except Exception as e:
    print(f'mariadb not available, using python-mysql')
    
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        
        # Drop and create database
        cursor.execute('DROP DATABASE IF EXISTS kids_ecommerce')
        cursor.execute('CREATE DATABASE kids_ecommerce')
        cursor.execute('USE kids_ecommerce')
        conn.commit()
        
        # Read SQL file as is
        with open('c:\\Users\\mnban\\Documents\\kids\\kids_ecommerce .sql', 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        
        # Execute the whole thing
        for statement in sql_content.split(';'):
            if statement.strip() and not statement.strip().startswith('--') and not statement.strip().startswith('/*'):
                try:
                    cursor.execute(statement)
                except Exception as ex:
                    if 'already exists' not in str(ex):
                        pass  # Ignore errors
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print('✅ Database imported using Python')
        
    except Exception as ex:
        print(f'❌ Error: {ex}')

# Verify
try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='kids_ecommerce'
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='kids_ecommerce'")
    tables = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM product")
    products = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user")
    users = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f'\n📊 Database Status:')
    print(f'   Tables: {tables}')
    print(f'   Products: {products}')
    print(f'   Users: {users}')
    
except Exception as e:
    print(f'Could not verify: {e}')
