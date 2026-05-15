from app import app, db, Order

with app.app_context():
    orders = Order.query.all()
    print(f'Total orders: {len(orders)}')
    for o in orders[:5]:
        print(f'Order {o.id}: User {o.buyer_id}, Status: {o.status}')
