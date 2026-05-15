"""
Fix PostgreSQL sequence and verify test users
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Fixing User Sequence and Verifying Test Users")
print("="*60)

with app.app_context():
    try:
        # Fix the sequence
        print("\n1. Fixing user ID sequence...")
        db.session.execute(text("""
            SELECT setval('user_id_seq', (SELECT MAX(id) FROM "user"));
        """))
        db.session.commit()
        print("   Sequence fixed!")
        
        # Check test users
        print("\n2. Checking test users...")
        
        test_emails = [
            'testbuyer@gmail.com',
            'testseller@gmail.com', 
            'testrider@gmail.com'
        ]
        
        for email in test_emails:
            result = db.session.execute(text("""
                SELECT id, first_name, last_name, role, status, email_verified
                FROM "user"
                WHERE email = :email
            """), {'email': email})
            
            user = result.fetchone()
            
            if user:
                print(f"\n   {user[3].upper()}: {email}")
                print(f"      ID: {user[0]}")
                print(f"      Name: {user[1]} {user[2]}")
                print(f"      Status: {user[4]}")
                print(f"      Verified: {user[5]}")
                
                # Make sure they're active and verified
                if user[4] != 'active' or not user[5]:
                    print(f"      Updating to active...")
                    db.session.execute(text("""
                        UPDATE "user"
                        SET status = 'active', email_verified = TRUE
                        WHERE email = :email
                    """), {'email': email})
                    db.session.commit()
                    print(f"      Updated!")
            else:
                print(f"\n   {email} - NOT FOUND")
                print(f"      Creating...")
                
                role = 'buyer' if 'buyer' in email else ('seller' if 'seller' in email else 'rider')
                first_name = 'Test'
                last_name = role.capitalize()
                
                result = db.session.execute(text("""
                    INSERT INTO "user" (email, password, first_name, last_name, phone, address, role, status, email_verified)
                    VALUES (:email, :password, :first_name, :last_name, '09123456789', 'Test Address', :role, 'active', TRUE)
                    RETURNING id
                """), {
                    'email': email,
                    'password': f'{last_name}123!',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role
                })
                user_id = result.scalar()
                db.session.commit()
                print(f"      Created! ID: {user_id}")
        
        # Get user IDs for test script
        print("\n" + "="*60)
        print("  Test User IDs (for test_chat_system.py)")
        print("="*60)
        
        for email in test_emails:
            result = db.session.execute(text("""
                SELECT id, role FROM "user" WHERE email = :email
            """), {'email': email})
            user = result.fetchone()
            if user:
                print(f"  {user[1].capitalize()}: ID {user[0]} - {email}")
        
        # Check if we have a test product
        print("\n" + "="*60)
        print("  Test Product")
        print("="*60)
        
        result = db.session.execute(text("""
            SELECT p.id, p.name, p.price, u.email as seller_email
            FROM product p
            JOIN "user" u ON p.seller_id = u.id
            WHERE u.email = 'testseller@gmail.com'
            AND p.status = 'active'
            LIMIT 1
        """))
        
        product = result.fetchone()
        
        if product:
            print(f"\n  Product ID: {product[0]}")
            print(f"  Name: {product[1]}")
            print(f"  Price: {product[2]}")
            print(f"  Seller: {product[3]}")
        else:
            print("\n  No test product found.")
            print("  Creating one...")
            
            # Get seller ID
            result = db.session.execute(text("""
                SELECT id FROM "user" WHERE email = 'testseller@gmail.com'
            """))
            seller = result.fetchone()
            
            if seller:
                # Get or create category
                result = db.session.execute(text("""
                    SELECT id FROM category WHERE status = 'active' LIMIT 1
                """))
                category = result.fetchone()
                
                if not category:
                    result = db.session.execute(text("""
                        INSERT INTO category (name, status)
                        VALUES ('Test Category', 'active')
                        RETURNING id
                    """))
                    category_id = result.scalar()
                    db.session.commit()
                else:
                    category_id = category[0]
                
                # Create product
                result = db.session.execute(text("""
                    INSERT INTO product (name, description, price, stock, category_id, seller_id, status)
                    VALUES ('Test Product', 'Test product for chat testing', 999.00, 10, :category_id, :seller_id, 'active')
                    RETURNING id
                """), {'category_id': category_id, 'seller_id': seller[0]})
                
                product_id = result.scalar()
                db.session.commit()
                print(f"  Created! Product ID: {product_id}")
        
        print("\n" + "="*60)
        print("  SUCCESS! Everything is ready")
        print("="*60)
        print("\nTest Credentials:")
        print("  Buyer:  testbuyer@gmail.com / Buyer123!")
        print("  Seller: testseller@gmail.com / Seller123!")
        print("  Rider:  testrider@gmail.com / Rider123!")
        print("\nNext step:")
        print("  python test_chat_system.py")
        print("="*60)
        
    except Exception as e:
        db.session.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*60)
        print("  Troubleshooting")
        print("="*60)
        print("\nIf you see 'connection timeout':")
        print("  - Check your internet connection")
        print("  - Verify Supabase is accessible")
        print("  - Try again in a moment")
        print("\nIf you see 'duplicate key':")
        print("  - The script already fixed the sequence")
        print("  - Users already exist, you can proceed")
        print("  - Run: python test_chat_system.py")
        print("="*60)
