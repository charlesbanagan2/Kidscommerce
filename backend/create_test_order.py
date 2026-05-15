from app import app, db, Order, User, Product, Cart, OrderItem
from datetime import datetime

with app.app_context():
    # Get test buyer
    buyer = User.query.filter_by(email='testbuyer@kidscommerce.com').first()
    
    # Get a product
    product = Product.query.first()
    
    if not product:
        print('No products found in database')
    else:
        # Create a test order
        order = Order(
            buyer_id=buyer.id,
            total_amount=product.price * 2,
            status='pending',
            payment_method='cod',
            payment_status='pending',
            shipping_address='Test Address 123',
            tracking_number=f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            price=product.price
        )
        
        db.session.add(order_item)
        db.session.commit()
        
        print(f'Test order created successfully')
        print(f'Order ID: {order.id}')
        print(f'Status: {order.status}')
        print(f'Total: {order.total_amount}')
