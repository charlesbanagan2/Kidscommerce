from app import app, db, Order, User, Product, OrderItem
from datetime import datetime

with app.app_context():
    # Get test buyer
    buyer = User.query.filter_by(email='testbuyer@kidscommerce.com').first()
    
    # Get a product
    product = Product.query.first()
    
    # Create a test order with delivered status
    order = Order(
        buyer_id=buyer.id,
        total_amount=product.price * 1,
        status='delivered',
        payment_method='cod',
        payment_status='paid',
        shipping_address='Test Address 789',
        tracking_number=f'DELIV-TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=1,
        price=product.price
    )
    
    db.session.add(order_item)
    db.session.commit()
    
    print(f'Delivered test order created for workflow test')
    print(f'Order ID: {order.id}')
    print(f'Status: {order.status}')
    print(f'Buyer: {buyer.email}')
