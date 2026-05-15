import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

from sqlalchemy import create_engine, text
from urllib.parse import quote

# Database connection
db_password = quote('Kidscommerce@1234')
db_url = f"postgresql+psycopg2://postgres:{db_password}@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres"

print("=" * 100)
print("FIXING OVER-RESERVED STOCK ISSUES")
print("=" * 100)

try:
    engine = create_engine(db_url)
    conn = engine.connect()
    
    # Find all products with over-reserved stock
    query = text("""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            p.stock as current_stock,
            SUM(oi.quantity) as total_reserved
        FROM product p
        JOIN order_item oi ON p.id = oi.product_id
        JOIN "order" o ON oi.order_id = o.id
        WHERE o.status IN ('pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit')
        GROUP BY p.id, p.name, p.stock
        HAVING SUM(oi.quantity) > p.stock
        ORDER BY p.id ASC
    """)
    
    result = conn.execute(query)
    over_reserved = result.fetchall()
    
    if not over_reserved:
        print("No over-reserved products found. All stock levels are correct!")
        conn.close()
        exit(0)
    
    print("\nPRODUCTS WITH OVER-RESERVED STOCK:")
    print("-" * 100)
    print(f"{'Product ID':<12} {'Product Name':<40} {'Stock':<10} {'Reserved':<10} {'Excess':<10}")
    print("-" * 100)
    
    for row in over_reserved:
        excess = row.total_reserved - row.current_stock
        print(f"{row.product_id:<12} {row.product_name[:40]:<40} {row.current_stock:<10} {row.total_reserved:<10} {excess:<10}")
    
    print("\n" + "=" * 100)
    print("SOLUTION: Cancel orders with excessive quantities")
    print("=" * 100)
    
    # For each over-reserved product, find orders with excessive quantities
    for row in over_reserved:
        product_id = row.product_id
        product_name = row.product_name
        current_stock = row.current_stock
        
        print(f"\nProduct: {product_name} (ID: {product_id})")
        print(f"Stock: {current_stock}")
        
        # Find orders for this product
        query2 = text("""
            SELECT 
                o.id as order_id,
                o.status,
                oi.quantity,
                o.buyer_id,
                o.created_at
            FROM "order" o
            JOIN order_item oi ON o.id = oi.order_id
            WHERE oi.product_id = :product_id
            AND o.status IN ('pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit')
            ORDER BY oi.quantity DESC, o.created_at ASC
        """)
        
        result2 = conn.execute(query2, {"product_id": product_id})
        orders = result2.fetchall()
        
        print(f"Found {len(orders)} active orders:")
        for order in orders:
            if order.quantity > current_stock:
                print(f"  Order {order.order_id}: {order.quantity} units (EXCESSIVE - should cancel)")
            else:
                print(f"  Order {order.order_id}: {order.quantity} units (OK)")
    
    print("\n" + "=" * 100)
    print("Do you want to cancel orders with excessive quantities? (yes/no)")
    print("=" * 100)
    
    user_input = input("Enter 'yes' to proceed: ").strip().lower()
    
    if user_input == 'yes':
        print("\nCancelling excessive orders...")
        
        for row in over_reserved:
            product_id = row.product_id
            current_stock = row.current_stock
            
            # Cancel orders with quantity > stock
            query3 = text("""
                UPDATE "order"
                SET status = 'cancelled', updated_at = NOW()
                WHERE id IN (
                    SELECT o.id
                    FROM "order" o
                    JOIN order_item oi ON o.id = oi.order_id
                    WHERE oi.product_id = :product_id
                    AND oi.quantity > :stock
                    AND o.status IN ('pending', 'to_pay', 'processing')
                )
            """)
            
            result3 = conn.execute(query3, {"product_id": product_id, "stock": current_stock})
            conn.commit()
            
            print(f"  Product {product_id}: Cancelled {result3.rowcount} orders")
        
        print("\nDone! Orders with excessive quantities have been cancelled.")
    else:
        print("\nCancelled. No changes made.")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
