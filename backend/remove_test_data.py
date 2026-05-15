"""
Remove test users and test products from database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Removing Test Users and Test Products")
print("="*60)

with app.app_context():
    try:
        test_emails = [
            'testbuyer@gmail.com',
            'testseller@gmail.com', 
            'testrider@gmail.com'
        ]
        
        # Remove test products first (foreign key constraint)
        print("\n1. Removing test products...")
        result = db.session.execute(text("""
            DELETE FROM product
            WHERE seller_id IN (
                SELECT id FROM "user" WHERE email IN :emails
            )
            RETURNING id, name
        """), {'emails': tuple(test_emails)})
        
        deleted_products = result.fetchall()
        if deleted_products:
            for prod in deleted_products:
                print(f"   [OK] Deleted product: {prod[1]} (ID: {prod[0]})")
        else:
            print("   No test products found")
        
        db.session.commit()
        
        # Remove test users
        print("\n2. Removing test users...")
        for email in test_emails:
            result = db.session.execute(text("""
                DELETE FROM "user"
                WHERE email = :email
                RETURNING id, first_name, last_name, role
            """), {'email': email})
            
            user = result.fetchone()
            if user:
                print(f"   [OK] Deleted {user[3]}: {user[1]} {user[2]} (ID: {user[0]})")
            else:
                print(f"   [-] {email} not found")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("  SUCCESS! Test data removed")
        print("="*60)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
