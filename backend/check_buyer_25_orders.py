from app import app, db, Order

with app.app_context():
    # Check orders for buyer_id 25
    orders = Order.query.filter_by(buyer_id=25).order_by(Order.created_at.desc()).all()
    
    print(f'\nTotal orders for buyer_id 25: {len(orders)}\n')
    
    for order in orders:
        print(f'Order ID: {order.id}')
        print(f'  Status: {order.status}')
        print(f'  Total: PHP {order.total_amount}')
        print(f'  Created: {order.created_at}')
        print(f'  Buyer ID: {order.buyer_id}')
        print('---')
