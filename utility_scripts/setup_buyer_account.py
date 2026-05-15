#!/usr/bin/env python3
"""
Create buyer account directly using SQLAlchemy
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from werkzeug.security import generate_password_hash

def create_buyer_account():
    """Create buyer test account"""
    with app.app_context():
        # Get the User model
        from sqlalchemy import text
        
        # Check if buyer already exists
        result = db.session.execute(
            text("SELECT * FROM user WHERE email = :email"),
            {"email": "buyer@test.com"}
        )
        buyer = result.fetchone()
        
        if buyer:
            print(f"✅ Buyer account already exists!")
            print(f"   ID: {buyer[0]}")
            print(f"   Email: {buyer[4]}")
            print(f"   Role: {buyer[9]}")
            return True
        
        # Create new buyer account
        try:
            password_hash = generate_password_hash('password123')
            
            db.session.execute(
                text("""
                    INSERT INTO user 
                    (username, first_name, last_name, email, password, phone, address, role, status, email_verified, created_at)
                    VALUES 
                    (:username, :first_name, :last_name, :email, :password, :phone, :address, :role, :status, :email_verified, :created_at)
                """),
                {
                    "username": "buyer_test",
                    "first_name": "Test",
                    "last_name": "Buyer",
                    "email": "buyer@test.com",
                    "password": password_hash,
                    "phone": "+1234567890",
                    "address": "123 Test Street, Test City",
                    "role": "buyer",
                    "status": "active",
                    "email_verified": True,
                    "created_at": text("NOW()")
                }
            )
            
            db.session.commit()
            
            print("✅ Buyer account created successfully!")
            print(f"   Email: buyer@test.com")
            print(f"   Password: password123")
            print(f"   Role: buyer")
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
