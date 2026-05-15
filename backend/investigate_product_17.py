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
    print("INVESTIGATING PRODUCT 17 - Play-Doh Airplane Explorer Starter Playset")
    print("=" * 120)
    
    # Check product details
    query1 = text("""
        SELECT id, name, stock, status, price, seller_id, category_id, created_at
        FROM product 
        WHERE id = 17
    """)
    
    result1 = conn.execute(query1)
    product = result1.fetchone()
    
    if product:
        print(f"\nPRODUCT DETAILS:")
        print(f"  ID: {product.id}")
        print(f"  Name: {product.name}")
        print(f"  Stock: {product.stock}")
        print(f"  Status: {product.status}")
        print(f"  Price: ${product.price}")
        print(f"  Seller ID: {product.seller_id}")
    else:
        print("ERROR: Product 17 not found!")
        exit(1)
    
    # Check all orders for this product
    print("\n" + "=" * 120)
    print("ALL ORDERS FOR PRODUCT 17")
    print("=" * 120)
    
    query2 = text("""
        SELECT 
            o.id as order_id,
            o.status as order_status,
            o.buyer_id,
            o.created_at,
            o.updated_at,
            oi.id as order_item_id,
            oi.quantity,
            oi.price_at_time,
            u.email as buyer_email
        FROM "order" o
        JOIN order_item oi ON o.id = oi.order_id
        LEFT JOIN "user" u ON o.buyer_id = u.id
        WHERE oi.product_id = 17
        ORDER BY o.created_at DESC
    """)
    
    result2 = conn.execute(query2)
    orders = result2.fetchall()
    
    if orders:
        print(f"{'Order ID':<10} {'Status':<20} {'Qty':<6} {'Buyer Email':<30} {'Created':<20}")
        print("-" * 120)
        
        total_all = 0
        total_active = 0
        total_completed = 0
        total_cancelled = 0
        
        for order in orders:
            total_all += order.quantity
            
            if order.order_status in ['pending', 'to_pay', 'processing', 'ready_for_pickup', 'to_ship', 'in_transit']:
                total_active += order.quantity
                status_marker = "ACTIVE"
            elif order.order_status in ['completed', 'delivered']:
                total_completed += order.quantity
                status_marker = "COMPLETED"
            elif order.order_status == 'cancelled':
                total_cancelled += order.quantity
                status_marker = "CANCELLED"
            else:
                status_marker = order.order_status.upper()
            
            print(f"{order.order_id:<10} {order.order_status:<20} {order.quantity:<6} {order.buyer_email[:30]:<30} {str(order.created_at)[:19]:<20} [{status_marker}]")
        
        print("-" * 120)
        print(f"Total Orders: {len(orders)}")
        print(f"Total Quantity (All): {total_all}")
        print(f"Total Quantity (Active): {total_active}")
        print(f"Total Quantity (Completed): {total_completed}")
        print(f"Total Quantity (Cancelled): {total_cancelled}")
    else:
        print("No orders found for this product.")
        total_active = 0
        total_completed = 0
    
    # Calculate available stock
    print("\n" + "=" * 120)
    print("STOCK CALCULATION")
    print("=" * 120)
    
    physical_stock = product.stock
    reserved_active = total_active
    reserved_completed = total_completed
    
    # Method 1: Current code logic
    available_method1 = physical_stock - reserved_completed - reserved_active
    
    print(f"\nMethod 1 (Current Code Logic):")
    print(f"  Physical Stock: {physical_stock}")
    print(f"  - Completed Orders: {reserved_completed}")
    print(f"  - Active Orders: {reserved_active}")
    print(f"  = Available: {available_method1}")
    
    # Method 2: Simple logic (stock - active only)
    available_method2 = physical_stock - reserved_active
    
    print(f"\nMethod 2 (Simple Logic - Active Only):")
    print(f"  Physical Stock: {physical_stock}")
    print(f"  - Active Orders: {reserved_active}")
    print(f"  = Available: {available_method2}")
    
    # Check for restock requests
    print("\n" + "=" * 120)
    print("RESTOCK REQUESTS")
    print("=" * 120)
    
    query3 = text("""
        SELECT id, product_id, requested_quantity, approved_quantity, status, created_at
        FROM restock_request
        WHERE product_id = 17
        ORDER BY created_at DESC
    """)
    
    result3 = conn.execute(query3)
    restock_requests = result3.fetchall()
    
    if restock_requests:
        print(f"{'ID':<6} {'Requested':<12} {'Approved':<12} {'Status':<15} {'Created':<20}")
        print("-" * 120)
        for rr in restock_requests:
            print(f"{rr.id:<6} {rr.requested_quantity:<12} {rr.approved_quantity or 0:<12} {rr.status:<15} {str(rr.created_at)[:19]:<20}")
        
        pending = [r for r in restock_requests if r.status == 'pending']
        if pending:
            print(f"\nWARNING: {len(pending)} pending restock request(s) found!")
            print("This will make the product show as unavailable until approved/rejected.")
    else:
        print("No restock requests found.")
    
    # Final recommendation
    print("\n" + "=" * 120)
    print("DIAGNOSIS & RECOMMENDATION")
    print("=" * 120)
    
    if available_method1 <= 0:
        print(f"\nPROBLEM FOUND: Available stock is {available_method1}")
        print("\nPossible causes:")
        print(f"1. Too many active orders ({reserved_active} units reserved)")
        print(f"2. Completed orders counted twice ({reserved_completed} units)")
        print(f"3. Pending restock request blocking availability")
        
        print("\nRECOMMENDED FIXES:")
        if reserved_completed > 0:
            print(f"1. Stock should be increased by completed orders: UPDATE product SET stock = {physical_stock + reserved_completed} WHERE id = 17;")
        if reserved_active > physical_stock:
            print(f"2. Cancel excess active orders (need to free {reserved_active - physical_stock} units)")
        if restock_requests and any(r.status == 'pending' for r in restock_requests):
            print(f"3. Approve or reject pending restock requests")
    else:
        print(f"\nStock calculation looks correct: {available_method1} units available")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
