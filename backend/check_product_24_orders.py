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
    print("ORDERS FOR PRODUCT ID 24 (Paw Patrol Sticky Catcher)")
    print("=" * 100)
    
    query = text("""
        SELECT 
            o.id as order_id,
            o.status as order_status,
            o.buyer_id,
            o.created_at,
            oi.quantity,
            oi.price_at_time,
            u.email as buyer_email
        FROM "order" o
        JOIN order_item oi ON o.id = oi.order_id
        LEFT JOIN "user" u ON o.buyer_id = u.id
        WHERE oi.product_id = 24
        ORDER BY o.created_at DESC
    """)
    
    result = conn.execute(query)
    
    print(f"{'Order ID':<10} {'Status':<20} {'Quantity':<10} {'Buyer Email':<30} {'Created':<20}")
    print("-" * 100)
    
    total_reserved = 0
    for row in result:
        total_reserved += row.quantity
        print(f"{row.order_id:<10} {row.order_status:<20} {row.quantity:<10} {row.buyer_email[:30]:<30} {str(row.created_at)[:19]:<20}")
    
    print("=" * 100)
    print(f"Total Quantity Reserved: {total_reserved}")
    print(f"Product Stock: 10")
    print(f"Available: 10 - {total_reserved} = {10 - total_reserved}")
    
    if total_reserved > 10:
        print("\nWARNING: Orders have reserved MORE stock than available!")
        print("This is causing the 'product not available' error.")
        print("\nSOLUTION OPTIONS:")
        print("1. Cancel excess orders")
        print("2. Increase product stock to match orders")
        print("3. Mark old orders as 'cancelled' if they are test data")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
