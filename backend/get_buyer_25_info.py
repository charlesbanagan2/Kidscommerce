from app import app, db, User

with app.app_context():
    buyer = User.query.filter_by(id=25).first()
    if buyer:
        print(f'Buyer ID: {buyer.id}')
        print(f'Email: {buyer.email}')
        print(f'Role: {buyer.role}')
        print(f'Status: {buyer.status}')
        print(f'First Name: {buyer.first_name}')
        print(f'Last Name: {buyer.last_name}')
    else:
        print('Buyer 25 not found')
