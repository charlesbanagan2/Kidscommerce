from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='charlesgabrielle.banagan@lspu.edu.ph').first()
    if user:
        print('User found in MySQL database:')
        print(f'ID: {user.id}')
        print(f'Name: {user.first_name} {user.last_name}')
        print(f'Email: {user.email}')
        print(f'Phone: {user.phone}')
        print(f'Address: {user.address}')
        print(f'Role: {user.role}')
        print(f'Status: {user.status}')
        print(f'Email Verified: {user.email_verified}')
    else:
        print('User NOT found in MySQL database')
