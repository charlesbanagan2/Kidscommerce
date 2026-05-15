import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, get_data, get_data_by_id, Product

with app.app_context():
    print("Diagnosing stock issues...\n")
    
    # Get active products
    products = Product.query.filter_by(status='active').limit(5).all()
    
    for p in products:
        print(f"Product ID: {p.id} - {p.name}")
        print(f"  Stock in database: {p.stock}")
        
        # Check pending restock
        pending = get_data('restock_request', filters={'product_id': p.id, 'status': 'pending'})
        if pending and len(pending) > 0:
            print(f"  WARNING: Has pending restock request - this causes 0 stock!")
            print(f"  Restock requests: {pending}")
        else:
            print(f"  No pending restock requests")
        
        # Check order items
        order_items = get_data('order_item', filters={'product_id': p.id})
        if order_items:
            print(f"  Order items: {len(order_items)}")
        else:
            print(f"  No order items")
        
        print()
    
    # Check all pending restock requests
    print("\n" + "="*60)
    print("ALL pending restock requests in system:")
    all_pending = get_data('restock_request', filters={'status': 'pending'})
    if all_pending:
        print(f"Found {len(all_pending)} pending requests")
        for req in all_pending:
            print(f"  ID: {req.get('id')} - Product: {req.get('product_id')} - Quantity: {req.get('quantity')}")
    else:
        print("No pending restock requests found")
