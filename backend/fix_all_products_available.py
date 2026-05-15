import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

from sqlalchemy import create_engine, text
from urllib.parse import quote

# Database connection
db_password = quote('Kidscommerce@1234')
db_url = f"postgresql+psycopg2://postgres:{db_password}@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres"

print("=" * 100)
print("FIXING ALL PRODUCTS TO BE AVAILABLE FOR BUYERS")
print("=" * 100)

try:
    engine = create_engine(db_url)
    conn = engine.connect()
    
    # Fix 1: Set Product 15 to 'active' status
    print("\nFix 1: Activating Product 15 (Hobby Tree Kiddie BZ Bus with Slide)")
    print("  Current status: pending")
    print("  New status: active")
    
    query1 = text("UPDATE product SET status = 'active' WHERE id = 15")
    conn.execute(query1)
    conn.commit()
    print("  DONE!")
    
    # Fix 2: Increase stock for Product 24 to make it available
    print("\nFix 2: Increasing stock for Product 24 (Paw Patrol Sticky Catcher Set)")
    print("  Current stock: 10")
    print("  Reserved by orders: 10")
    print("  New stock: 20 (will make 10 units available)")
    
    query2 = text("UPDATE product SET stock = 20 WHERE id = 24")
    conn.execute(query2)
    conn.commit()
    print("  DONE!")
    
    # Verify the fixes
    print("\n" + "=" * 100)
    print("VERIFICATION - CHECKING ALL PRODUCTS")
    print("=" * 100)
    
    query3 = text("""
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
    
    result = conn.execute(query3)
    
    print(f"{'ID':<5} {'Name':<45} {'Stock':<8} {'Reserved':<10} {'Available':<10} {'Status':<15}")
    print("-" * 100)
    
    available_count = 0
    unavailable_count = 0
    
    for row in result:
        if row.buyer_status == 'AVAILABLE':
            available_count += 1
            status_display = "AVAILABLE"
        else:
            unavailable_count += 1
            status_display = row.buyer_status
        
        print(f"{row.id:<5} {row.name[:45]:<45} {row.physical_stock:<8} {row.reserved:<10} {row.available_stock:<10} {status_display:<15}")
    
    print("=" * 100)
    print(f"\nRESULTS:")
    print(f"  Total Products: {available_count + unavailable_count}")
    print(f"  Available to Buyers: {available_count}")
    print(f"  Unavailable to Buyers: {unavailable_count}")
    
    if unavailable_count == 0:
        print("\n" + "=" * 100)
        print("SUCCESS! ALL 24 PRODUCTS ARE NOW AVAILABLE TO BUYERS!")
        print("=" * 100)
    else:
        print("\nWARNING: Some products are still unavailable. Check the list above.")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
