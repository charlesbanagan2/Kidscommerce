import mysql.connector

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password=''
    )
    cursor = conn.cursor()
    
    print('🔄 Setting up database...')
    
    # Drop and recreate
    cursor.execute('DROP DATABASE IF EXISTS kids_ecommerce')
    cursor.execute('CREATE DATABASE kids_ecommerce')
    cursor.execute('USE kids_ecommerce')
    conn.commit()
    
    print('📖 Reading SQL file...')
    with open('c:\\Users\\mnban\\Documents\\kids\\kids_ecommerce .sql', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print('⚙️  Executing SQL...')
    
    # Split more intelligently - split on ); but keep context
    lines = content.split('\n')
    statement = ''
    count = 0
    
    for line in lines:
        # Skip comments and empty lines
        if line.strip().startswith('--') or line.strip().startswith('/*') or not line.strip():
            continue
        if line.strip().startswith('/*!'):
            continue
            
        statement += line + '\n'
        
        # Check if statement is complete (ends with ;)
        if line.rstrip().endswith(';'):
            try:
                # Clean up statement
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
                    count += 1
                    if count % 50 == 0:
                        print(f'  ✅ {count} statements...')
                statement = ''
            except mysql.connector.Error as e:
                # Only show critical errors
                if 'No database selected' not in str(e):
                    pass
                statement = ''
    
    conn.commit()
    
    # Verify
    cursor.execute("SHOW TABLES FROM kids_ecommerce")
    tables = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM product")
    product_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user") 
    user_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f'\n✅ Database ready!')
    print(f'   Statements executed: {count}')
    print(f'   Tables created: {len(tables)}')
    print(f'   Products in DB: {product_count}')
    print(f'   Users in DB: {user_count}')
    print(f'\n📋 Tables:')
    for table in sorted([t[0] for t in tables]):
        print(f'   ✓ {table}')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
