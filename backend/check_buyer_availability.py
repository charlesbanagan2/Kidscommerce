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
    
    print("=" * 120)
    print("PRODUCT AVAILABILITY CHECK FOR BUYERS")
    print("=" * 120)
    
    # Query all products with calculated available stock
    query = text("""
        WITH order_reservations AS (
            SELECT 
                oi.product_id,
                SUM(oi.quantity) as reserved_qty
            FROM order_item oi
            JOIN "order" o ON oi.order_id = o.id
            WHERE o.status IN ('pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit', 'delivered')
            GROUP BY oi.product_id
        )
        SELECT 
            p.id,
            p.name,
            p.stock as physical_stock,
            p.status,
            p.price,
            COALESCE(r.reserved_qty, 0) as reserved,
            (p.stock - COALESCE(r.reserved_qty, 0)) as available_stock,
            CASE 
                WHEN p.status != 'active' THEN 'NOT ACTIVE'
                WHEN (p.stock - COALESCE(r.reserved_qty, 0)) <= 0 THEN 'OUT OF STOCK'
                ELSE 'AVAILABLE'
            END as buyer_status
        FROM product p
        LEFT JOIN order_reservations r ON p.id = r.product_id
        ORDER BY p.id ASC
    """)
    
    result = conn.execute(query)
    
    print(f"{'ID':<5} {'Name':<40} {'Stock':<8} {'Reserved':<10} {'Available':<10} {'Status':<12} {'Buyer Status':<15}")
    print("-" * 120)
    
    total = 0
    available_count = 0
    unavailable_count = 0
    not_active_count = 0
    
    unavailable_products = []
    
    for row in result:
        total += 1
        
        if row.buyer_status == 'AVAILABLE':
            available_count += 1
            status_display = "AVAILABLE"
        elif row.buyer_status == 'NOT ACTIVE':
            not_active_count += 1
            unavailable_count += 1
            status_display = "NOT ACTIVE"
            unavailable_products.append({
                'id': row.id,
                'name': row.name,
                'reason': 'Product status is not active',
                'stock': row.physical_stock,
                'reserved': row.reserved,
                'available': row.available_stock,
                'status': row.status
            })
        else:
            unavailable_count += 1
            status_display = "OUT OF STOCK"
            unavailable_products.append({
                'id': row.id,
                'name': row.name,
                'reason': 'All stock reserved by orders',
                'stock': row.physical_stock,
                'reserved': row.reserved,
                'available': row.available_stock,
                'status': row.status
            })
        
        print(f"{row.id:<5} {row.name[:40]:<40} {row.physical_stock:<8} {row.reserved:<10} {row.available_stock:<10} {row.status:<12} {status_display:<15}")
    
    print("=" * 120)
    print(f"\nSUMMARY:")
    print(f"  Total Products: {total}")
    print(f"  Available to Buyers: {available_count}")
    print(f"  Unavailable to Buyers: {unavailable_count}")
    print(f"    - Not Active: {not_active_count}")
    print(f"    - Out of Stock: {unavailable_count - not_active_count}")
    
    if unavailable_products:
        print("\n" + "=" * 120)
        print("PRODUCTS UNAVAILABLE TO BUYERS - DETAILS")
        print("=" * 120)
        
        for prod in unavailable_products:
            print(f"\nProduct ID {prod['id']}: {prod['name']}")
            print(f"  Reason: {prod['reason']}")
            print(f"  Physical Stock: {prod['stock']}")
            print(f"  Reserved by Orders: {prod['reserved']}")
            print(f"  Available: {prod['available']}")
            print(f"  Status: {prod['status']}")
            
            if prod['status'] != 'active':
                print(f"  FIX: UPDATE product SET status = 'active' WHERE id = {prod['id']};")
            elif prod['available'] <= 0:
                needed = prod['reserved'] - prod['stock']
                print(f"  FIX Option 1: UPDATE product SET stock = {prod['reserved']} WHERE id = {prod['id']};")
                print(f"  FIX Option 2: Cancel orders reserving this product")
    
    # Check for orders that need attention
    print("\n" + "=" * 120)
    print("ORDERS RESERVING STOCK")
    print("=" * 120)
    
    query2 = text("""
        SELECT 
            o.id as order_id,
            o.status,
            o.buyer_id,
            o.created_at,
            p.id as product_id,
            p.name as product_name,
            oi.quantity,
            p.stock as product_stock
        FROM "order" o
        JOIN order_item oi ON o.id = oi.order_id
        JOIN product p ON oi.product_id = p.id
        WHERE o.status IN ('pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit', 'delivered')
        ORDER BY p.id ASC, o.created_at DESC
    """)
    
    result2 = conn.execute(query2)
    
    print(f"{'Order ID':<10} {'Product ID':<12} {'Product Name':<35} {'Qty':<6} {'Stock':<8} {'Status':<15}")
    print("-" * 120)
    
    for row in result2:
        print(f"{row.order_id:<10} {row.product_id:<12} {row.product_name[:35]:<35} {row.quantity:<6} {row.product_stock:<8} {row.status:<15}")
    
    conn.close()
    
    print("\n" + "=" * 120)
    print("RECOMMENDATION")
    print("=" * 120)
    
    if unavailable_count == 0:
        print("All products are AVAILABLE to buyers!")
    else:
        print(f"{unavailable_count} products are UNAVAILABLE to buyers.")
        print("\nTo make ALL products available:")
        print("1. Set all products to 'active' status")
        print("2. Ensure stock >= reserved quantity for each product")
        print("3. Or cancel test/old orders to free up stock")
        print("\nRun the fix script:")
        print("  python fix_all_products_available.py")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
