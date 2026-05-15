import mysql.connector
import re

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password=''
    )
    cursor = conn.cursor()
    
    # Drop and create database
    print('🔄 Dropping and creating database...')
    cursor.execute('DROP DATABASE IF EXISTS kids_ecommerce')
    cursor.execute('CREATE DATABASE kids_ecommerce')
    conn.commit()
    
    # Read SQL file
    print('📖 Reading SQL file...')
    with open('c:\\Users\\mnban\\Documents\\kids\\kids_ecommerce .sql', 'r', encoding='utf-8', errors='ignore') as f:
        sql_content = f.read()
    
    # Parse SQL more carefully
    print('⚙️  Parsing SQL...')
    
    # Remove comments
    sql_content = re.sub(r'--.*?\n', '\n', sql_content)  # Remove line comments
    sql_content = re.sub(r'/\*[\s\S]*?\*/', '', sql_content)  # Remove block comments
    
    # Split by semicolon but preserve the statements
    statements = []
    current = ''
    for char in sql_content:
        if char == ';':
            if current.strip():
                statements.append(current.strip())
            current = ''
        else:
            current += char
    
    if current.strip():
        statements.append(current.strip())
    
    # Execute statements
    print(f'📊 Found {len(statements)} SQL statements')
    print('🚀 Executing statements...\n')
    
    executed = 0
    skipped = 0
    
    for i, statement in enumerate(statements):
        if not statement:
            continue
            
        # Skip directives
        if statement.startswith('/*!'):
            skipped += 1
            continue
        
        try:
            cursor.execute(statement)
            executed += 1
            
            if executed % 20 == 0:
                print(f'  ✅ Executed {executed} statements...')
            
        except mysql.connector.Error as e:
            # Only show errors that aren't expected
            if 'already exists' not in str(e) and 'Duplicate' not in str(e):
                print(f'  ⚠️  Error in statement {i+1}: {e}')
            skipped += 1
    
    conn.commit()
    
    # Verify database
    cursor.execute('USE kids_ecommerce')
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='kids_ecommerce'")
    table_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM product")
    product_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user")
    user_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f'\n✅ Database restored successfully!')
    print(f'   Statements executed: {executed}')
    print(f'   Tables created: {table_count}')
    print(f'   Products: {product_count}')
    print(f'   Users: {user_count}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
