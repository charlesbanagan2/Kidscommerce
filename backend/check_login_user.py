from app import app, db, User

with app.app_context():
    email = 'malakaslang53@gmail.com'
    user = User.query.filter_by(email=email).first()
    
    if user:
        print(f'User found:')
        print(f'  ID: {user.id}')
        print(f'  Email: {user.email}')
        print(f'  First Name: {user.first_name}')
        print(f'  Last Name: {user.last_name}')
        print(f'  Role: {user.role}')
        print(f'  Status: {user.status}')
        print(f'  Password hash: {user.password[:50]}...')
    else:
        print(f'User not found with email: {email}')
