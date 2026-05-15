from app import app, db, User, bcrypt

with app.app_context():
    # Check if test buyer exists
    test_buyer = User.query.filter_by(email='testbuyer@kidscommerce.com').first()
    
    if test_buyer:
        print('Test buyer already exists')
        print(f'Email: {test_buyer.email}')
        print(f'ID: {test_buyer.id}')
        print(f'Role: {test_buyer.role}')
        print(f'Status: {test_buyer.status}')
    else:
        # Create test buyer with fresh bcrypt hash
        password = 'Test12345@'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        test_buyer = User(
            first_name='Test',
            last_name='Buyer',
            email='testbuyer@kidscommerce.com',
            password=hashed_password,
            phone='09123456789',
            address='Test Address',
            role='buyer',
            status='active',
            email_verified=True
        )
        
        db.session.add(test_buyer)
        db.session.commit()
        
        print('Test buyer created successfully')
        print(f'Email: testbuyer@kidscommerce.com')
        print(f'Password: Test12345@')
        print(f'ID: {test_buyer.id}')
