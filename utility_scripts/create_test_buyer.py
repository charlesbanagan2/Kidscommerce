#!/usr/bin/env python
"""Create a test buyer account for login testing"""
import sys
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')

from app import app, db, User
import bcrypt

def hash_password(password):
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with app.app_context():
    # Check if test buyer already exists
    existing = User.query.filter_by(email='testbuyer@test.com').first()
    if existing:
        print("✓ Test buyer already exists")
        print(f"  Email: {existing.email}")
        print(f"  Role: {existing.role}")
        print(f"  Status: {existing.status}")
        sys.exit(0)
    
    # Create test buyer account
    test_buyer = User(
        email='testbuyer@test.com',
        password=hash_password('test123'),  # Hashed password
        first_name='Test',
        last_name='Buyer',
        phone='09123456789',
        role='buyer',
        status='active',  # Auto-activate for testing
        email_verified=True
    )
    
    db.session.add(test_buyer)
    db.session.commit()
    
    print("✓ Test buyer account created successfully!")
    print(f"  Email: testbuyer@test.com")
    print(f"  Password: test123")
    print(f"  Role: buyer")
    print(f"  Status: active")
    print(f"  Phone: 09123456789")
