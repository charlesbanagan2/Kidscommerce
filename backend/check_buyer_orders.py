from app import app, db, Order, User

with app.app_context():
    # Find buyers with orders
    buyers_with_orders = db.session.query(User.id, User.email, User.first_name, User.last_name).join(Order, User.id == Order.buyer_id).distinct().all()
    
    print('Buyers with orders:')
    for buyer in buyers_with_orders:
        user_id, email, first_name, last_name = buyer
        orders = Order.query.filter_by(buyer_id=user_id).all()
        print(f'  User {user_id}: {email} ({first_name} {last_name}) - {len(orders)} orders')
        for order in orders[:3]:
            print(f'    Order {order.id}: Status {order.status}')
