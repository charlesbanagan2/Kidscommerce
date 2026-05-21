from app import app, db, Order
from datetime import datetime

with app.app_context():
    # Simulate what the API does
    buyer_id = 25
    
    # Get all orders for buyer 25
    all_orders = Order.query.filter_by(buyer_id=buyer_id).order_by(Order.created_at.desc()).all()
    
    print(f'\nTotal orders for buyer {buyer_id}: {len(all_orders)}\n')
    
    # Group by status (matching the API logic)
    to_pay = [o for o in all_orders if o.status in ['pending', 'to_pay']]
    to_ship = [o for o in all_orders if o.status in ['processing', 'ready_for_pickup']]
    to_receive = [o for o in all_orders if o.status in ['to_ship', 'in_transit', 'delivered']]
    completed = [o for o in all_orders if o.status == 'completed']
    returns = [o for o in all_orders if o.status in ['return_requested', 'returned', 'refunded']]
    cancelled = [o for o in all_orders if o.status == 'cancelled']
    
    print('Orders by status:')
    print(f'  to_pay: {len(to_pay)} orders')
    for o in to_pay[:5]:
        print(f'    Order #{o.id}: {o.status} - PHP {o.total_amount}')
    
    print(f'\n  to_ship: {len(to_ship)} orders')
    for o in to_ship[:5]:
        print(f'    Order #{o.id}: {o.status} - PHP {o.total_amount}')
    
    print(f'\n  to_receive: {len(to_receive)} orders')
    for o in to_receive[:5]:
        print(f'    Order #{o.id}: {o.status} - PHP {o.total_amount}')
    
    print(f'\n  completed: {len(completed)} orders')
    for o in completed[:5]:
        print(f'    Order #{o.id}: {o.status} - PHP {o.total_amount}')
    
    print(f'\n  returns: {len(returns)} orders')
    print(f'  cancelled: {len(cancelled)} orders')
    
    print(f'\n\nChecking orders 56 and 57 specifically:')
    for order_id in [56, 57]:
        order = Order.query.get(order_id)
        if order:
            print(f'\nOrder #{order.id}:')
            print(f'  Status: {order.status}')
            print(f'  Buyer ID: {order.buyer_id}')
            print(f'  Total: PHP {order.total_amount}')
            print(f'  Created: {order.created_at}')
            print(f'  Should be in to_pay: {order.status in ["pending", "to_pay"]}')
