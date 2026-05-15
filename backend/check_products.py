import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

from sqlalchemy import create_engine, text
from urllib.parse import quote

# Database connection
db_password = quote('Kidscommerce@1234')
db_url = f"postgresql+psycopg2://postgres:{db_password}@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres"

try:
    engine = create_engine(db_url)
    conn = engine.connect()
    
    # Query products
    query = text("SELECT id, name, stock, status FROM product ORDER BY id ASC")
    result = conn.execute(query)
    
    print("=" * 80)
    print("PRODUCTS IN SUPABASE DATABASE")
    print("=" * 80)
    print(f"{'ID':<5} {'Name':<40} {'Stock':<10} {'Status':<10}")
    print("-" * 80)
    
    for row in result:
        print(f"{row.id:<5} {row.name[:40]:<40} {row.stock:<10} {row.status:<10}")
    
    print("=" * 80)
    
    # Count products by status
    query2 = text("SELECT status, COUNT(*) as count FROM product GROUP BY status")
    result2 = conn.execute(query2)
    
    print("\nPRODUCT COUNT BY STATUS:")
    print("-" * 40)
    for row in result2:
        print(f"{row.status}: {row.count}")
    
    conn.close()
    print("\n✅ Database query successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
