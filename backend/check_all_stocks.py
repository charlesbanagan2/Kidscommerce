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
    
    print("=" * 100)
    print("ALL PRODUCTS IN DATABASE - STOCK CHECK")
    print("=" * 100)
    
    # Query all products
    query = text("""
        SELECT id, name, stock, status, price, seller_id, category_id
        FROM product 
        ORDER BY id ASC
    """)
    result = conn.execute(query)
    
    print(f"{'ID':<5} {'Name':<45} {'Stock':<8} {'Status':<10} {'Price':<10}")
    print("-" * 100)
    
    total_products = 0
    active_products = 0
    in_stock_products = 0
    out_of_stock_products = 0
    
    for row in result:
        total_products += 1
        if row.status == 'active':
            active_products += 1
        if row.stock > 0:
            in_stock_products += 1
            stock_indicator = "IN STOCK"
        else:
            out_of_stock_products += 1
            stock_indicator = "OUT OF STOCK"
        
        print(f"{row.id:<5} {row.name[:45]:<45} {row.stock:<8} {row.status:<10} ${row.price:<9.2f}")
    
    print("=" * 100)
    print("\nSUMMARY:")
    print("-" * 50)
    print(f"Total Products: {total_products}")
    print(f"Active Products: {active_products}")
    print(f"Pending Products: {total_products - active_products}")
    print(f"In Stock (stock > 0): {in_stock_products}")
    print(f"Out of Stock (stock = 0): {out_of_stock_products}")
    
    # Check for orders that might be reserving stock
    print("\n" + "=" * 100)
    print("CHECKING ACTIVE ORDERS (Stock Reservations)")
    print("=" * 100)
    
    query2 = text("""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            p.stock as current_stock,
            COUNT(oi.id) as order_count,
            SUM(oi.quantity) as reserved_quantity,
            o.status as order_status
        FROM product p
        LEFT JOIN order_item oi ON p.id = oi.product_id
        LEFT JOIN "order" o ON oi.order_id = o.id
        WHERE o.status IN ('pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit')
        GROUP BY p.id, p.name, p.stock, o.status
        ORDER BY p.id ASC
    """)
    
    result2 = conn.execute(query2)
    rows = result2.fetchall()
    
    if rows:
        print(f"{'Product ID':<12} {'Product Name':<35} {'Stock':<8} {'Reserved':<10} {'Order Status':<15}")
        print("-" * 100)
        for row in rows:
            print(f"{row.product_id:<12} {row.product_name[:35]:<35} {row.current_stock:<8} {row.reserved_quantity:<10} {row.order_status:<15}")
    else:
        print("No active orders reserving stock.")
    
    # Check products with low stock
    print("\n" + "=" * 100)
    print("PRODUCTS WITH LOW STOCK (Stock <= 10)")
    print("=" * 100)
    
    query3 = text("""
        SELECT id, name, stock, status
        FROM product 
        WHERE stock <= 10 AND stock > 0
        ORDER BY stock ASC, id ASC
    """)
    
    result3 = conn.execute(query3)
    low_stock_rows = result3.fetchall()
    
    if low_stock_rows:
        print(f"{'ID':<5} {'Name':<50} {'Stock':<8} {'Status':<10}")
        print("-" * 100)
        for row in low_stock_rows:
            print(f"{row.id:<5} {row.name[:50]:<50} {row.stock:<8} {row.status:<10}")
        print(f"\nTotal Low Stock Products: {len(low_stock_rows)}")
    else:
        print("No products with low stock.")
    
    # Check products that are out of stock
    print("\n" + "=" * 100)
    print("PRODUCTS OUT OF STOCK (Stock = 0)")
    print("=" * 100)
    
    query4 = text("""
        SELECT id, name, stock, status
        FROM product 
        WHERE stock = 0
        ORDER BY id ASC
    """)
    
    result4 = conn.execute(query4)
    out_of_stock_rows = result4.fetchall()
    
    if out_of_stock_rows:
        print(f"{'ID':<5} {'Name':<50} {'Stock':<8} {'Status':<10}")
        print("-" * 100)
        for row in out_of_stock_rows:
            print(f"{row.id:<5} {row.name[:50]:<50} {row.stock:<8} {row.status:<10}")
        print(f"\nTotal Out of Stock Products: {len(out_of_stock_rows)}")
    else:
        print("All products have stock available!")
    
    conn.close()
    print("\n" + "=" * 100)
    print("DATABASE CHECK COMPLETE")
    print("=" * 100)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
