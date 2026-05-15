"""
Simple script to create test users for chat system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Creating Test Users")
print("="*60)

with app.app_context():
    test_users = [
        ('testbuyer@gmail.com', 'Buyer123!', 'Test', 'Buyer', 'buyer'),
        ('testseller@gmail.com', 'Seller123!', 'Test', 'Seller', 'seller'),
        ('testrider@gmail.com', 'Rider123!', 'Test', 'Rider', 'rider')
    ]
    
    for email, password, first_name, last_name, role in test_users:
        try:
            # Check if user exists
            result = db.session.execute(text("""
                SELECT id, status FROM "user" WHERE email = :email
            """), {'email': email})
            
            user = result.fetchone()
            
            if user:
                print(f"\n{role.capitalize()}: {email}")
                print(f"  Already exists (ID: {user[0]}, Status: {user[1]})")
                
                # Update to active
                db.session.execute(text("""
                    UPDATE "user" 
                    SET status = 'active', email_verified = TRUE
                    WHERE email = :email
                """), {'email': email})
                db.session.commit()
                print(f"  Updated to active")
            else:
                # Create new user
                result = db.session.execute(text("""
                    INSERT INTO "user" (email, password, first_name, last_name, phone, address, role, status, email_verified)
                    VALUES (:email, :password, :first_name, :last_name, '09123456789', 'Test Address', :role, 'active', TRUE)
                    RETURNING id
                """), {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role
                })
                user_id = result.scalar()
                db.session.commit()
                print(f"\n{role.capitalize()}: {email}")
                print(f"  Created (ID: {user_id})")
        
        except Exception as e:
            db.session.rollback()
            print(f"\nError with {role}: {e}")

print("\n" + "="*60)
print("  Test Credentials")
print("="*60)
print("\nBuyer:  testbuyer@gmail.com / Buyer123!")
print("Seller: testseller@gmail.com / Seller123!")
print("Rider:  testrider@gmail.com / Rider123!")
print("\n" + "="*60)
print("  Done! Now run: python test_chat_system.py")
print("="*60)
