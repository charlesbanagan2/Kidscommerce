#!/usr/bin/env python3
"""
Create buyer account directly in database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_buyer_account():
    with app.app_context():
        # Check if buyer already exists
        buyer = User.query.filter_by(email='buyer@test.com').first()
        
        if buyer:
            print(f"✅ Buyer account already exists!")
            print(f"   Email: {buyer.email}")
            print(f"   Role: {buyer.role}")
            print(f"   ID: {buyer.id}")
            return True
        
        # Create new buyer account
        try:
            buyer = User(
                email='buyer@test.com',
                password=generate_password_hash('password123'),
                username='buyer_test',
                first_name='Test',
                last_name='Buyer',
                phone='+1234567890',
                address='123 Test Street',
                role='buyer',
                status='active',
                email_verified=True,
                two_factor_enabled=False
            )
            
            db.session.add(buyer)
            db.session.commit()
            
            print("✅ Buyer account created successfully!")
            print(f"   Email: buyer@test.com")
            print(f"   Password: password123")
            print(f"   ID: {buyer.id}")
            print(f"   Role: {buyer.role}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating buyer account: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Creating Test Buyer Account")
    print("=" * 60)
    print()
    
    success = create_buyer_account()
    
    print()
    print("=" * 60)
    if success:
        print("Ready for login testing!")
        sys.exit(0)
    else:
        print("Failed to create account")
        sys.exit(1)
