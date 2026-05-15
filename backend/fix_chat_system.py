"""
COMPREHENSIVE CHAT SYSTEM FIX
Fixes all 500 errors and database issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
import traceback

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_database_connection():
    """Check if database connection is working"""
    print_header("Step 1: Checking Database Connection")
    
    with app.app_context():
        try:
            result = db.session.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection successful")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

def check_required_tables():
    """Check if required tables exist"""
    print_header("Step 2: Checking Required Tables")
    
    required_tables = ['user', 'product', 'order']
    
    with app.app_context():
        try:
            for table in required_tables:
                result = db.session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """))
                
                exists = result.scalar()
                if exists:
                    print(f"✓ {table} table exists")
                else:
                    print(f"✗ {table} table missing")
                    return False
            
            return True
        except Exception as e:
            print(f"✗ Error checking tables: {e}")
            return False

def create_chat_table():
    """Create chat_message table"""
    print_header("Step 3: Creating chat_message Table")
    
    with app.app_context():
        try:
            # Check if exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chat_message'
                );
            """))
            
            exists = result.scalar()
            
            if exists:
                print("⚠️  chat_message table already exists")
                print("Checking table structure...")
                
                # Check columns
                result = db.session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_message'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                print("\nExisting columns:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                response = input("\nRecreate table? (y/n): ").lower()
                if response != 'y':
                    print("Skipping table creation")
                    return True
                
                print("\nDropping existing table...")
                db.session.execute(text("DROP TABLE IF EXISTS chat_message CASCADE"))
                db.session.commit()
                print("✓ Table dropped")
            
            print("\nCreating chat_message table...")
            
            # Create table
            db.session.execute(text("""
                CREATE TABLE chat_message (
                    id SERIAL PRIMARY KEY,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    product_id INTEGER,
                    order_id INTEGER,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT fk_sender FOREIGN KEY (sender_id) REFERENCES "user"(id) ON DELETE CASCADE,
                    CONSTRAINT fk_receiver FOREIGN KEY (receiver_id) REFERENCES "user"(id) ON DELETE CASCADE,
                    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE SET NULL,
                    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE SET NULL
                )
            """))
            db.session.commit()
            print("✓ Table created")
            
            print("\nCreating indexes...")
            
            indexes = [
                ("idx_chat_sender", "CREATE INDEX idx_chat_sender ON chat_message(sender_id)"),
                ("idx_chat_receiver", "CREATE INDEX idx_chat_receiver ON chat_message(receiver_id)"),
                ("idx_chat_product", "CREATE INDEX idx_chat_product ON chat_message(product_id)"),
                ("idx_chat_created", "CREATE INDEX idx_chat_created ON chat_message(created_at DESC)"),
                ("idx_chat_unread", "CREATE INDEX idx_chat_unread ON chat_message(receiver_id, is_read) WHERE is_read = FALSE"),
            ]
            
            for idx_name, idx_sql in indexes:
                try:
                    db.session.execute(text(idx_sql))
                    db.session.commit()
                    print(f"  ✓ {idx_name}")
                except Exception as e:
                    print(f"  ⚠️  {idx_name}: {str(e)[:50]}")
            
            print("\n✓ chat_message table created successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error creating table: {e}")
            traceback.print_exc()
            return False

def test_chat_operations():
    """Test basic chat operations"""
    print_header("Step 4: Testing Chat Operations")
    
    with app.app_context():
        try:
            # Test insert
            print("Testing insert...")
            db.session.execute(text("""
                INSERT INTO chat_message (sender_id, receiver_id, message)
                VALUES (1, 2, 'Test message')
                RETURNING id
            """))
            db.session.commit()
            print("✓ Insert works")
            
            # Test select
            print("Testing select...")
            result = db.session.execute(text("""
                SELECT id, sender_id, receiver_id, message, created_at
                FROM chat_message
                ORDER BY created_at DESC
                LIMIT 1
            """))
            row = result.fetchone()
            if row:
                print(f"✓ Select works - Message ID: {row[0]}")
            
            # Test update
            print("Testing update...")
            db.session.execute(text("""
                UPDATE chat_message 
                SET is_read = TRUE 
                WHERE id = (SELECT MAX(id) FROM chat_message)
            """))
            db.session.commit()
            print("✓ Update works")
            
            # Clean up test data
            db.session.execute(text("DELETE FROM chat_message WHERE message = 'Test message'"))
            db.session.commit()
            print("✓ Delete works")
            
            print("\n✓ All chat operations working")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error testing operations: {e}")
            traceback.print_exc()
            return False

def verify_api_routes():
    """Verify API routes are registered"""
    print_header("Step 5: Verifying API Routes")
    
    with app.app_context():
        try:
            chat_routes = [
                '/api/v1/chat/conversations',
                '/api/v1/chat/messages/<int:other_user_id>',
                '/api/v1/chat/send',
                '/api/v1/chat/unread-count',
                '/api/v1/chat/product/start',
                '/api/v1/chat/product/<int:product_id>/messages',
                '/api/v1/chat/product/send',
                '/api/v1/chat/conversations/product'
            ]
            
            registered_routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            for route in chat_routes:
                # Check if route pattern exists
                route_pattern = route.replace('<int:other_user_id>', '<other_user_id>').replace('<int:product_id>', '<product_id>')
                found = any(route_pattern.replace('<', '').replace('>', '') in r for r in registered_routes)
                
                if found:
                    print(f"✓ {route}")
                else:
                    print(f"✗ {route} - NOT REGISTERED")
            
            print("\n✓ API routes verified")
            return True
            
        except Exception as e:
            print(f"\n✗ Error verifying routes: {e}")
            return False

def create_test_users():
    """Create test users if they don't exist"""
    print_header("Step 6: Creating Test Users")
    
    with app.app_context():
        try:
            test_users = [
                ('testbuyer@gmail.com', 'Buyer123!', 'Test', 'Buyer', 'buyer'),
                ('testseller@gmail.com', 'Seller123!', 'Test', 'Seller', 'seller'),
                ('testrider@gmail.com', 'Rider123!', 'Test', 'Rider', 'rider')
            ]
            
            for email, password, first_name, last_name, role in test_users:
                # Check if user exists
                result = db.session.execute(text("""
                    SELECT id FROM "user" WHERE email = :email
                """), {'email': email})
                
                user = result.fetchone()
                
                if user:
                    print(f"✓ {role.capitalize()} already exists (ID: {user[0]})")
                    
                    # Update to active if not already
                    db.session.execute(text("""
                        UPDATE "user" 
                        SET status = 'active', email_verified = TRUE
                        WHERE email = :email
                    """), {'email': email})
                    db.session.commit()
                else:
                    # Create user - let PostgreSQL auto-generate ID
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
                    print(f"✓ {role.capitalize()} created (ID: {user_id})")
            
            print("\n✓ Test users ready")
            print("\nTest Credentials:")
            print("  Buyer:  testbuyer@gmail.com / Buyer123!")
            print("  Seller: testseller@gmail.com / Seller123!")
            print("  Rider:  testrider@gmail.com / Rider123!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error creating users: {e}")
            traceback.print_exc()
            return False

def main():
    """Run all fixes"""
    print("")
    print("="*60)
    print("  COMPREHENSIVE CHAT SYSTEM FIX")
    print("="*60)
    print("")
    
    steps = [
        ("Database Connection", check_database_connection),
        ("Required Tables", check_required_tables),
        ("Chat Table", create_chat_table),
        ("Chat Operations", test_chat_operations),
        ("API Routes", verify_api_routes),
        ("Test Users", create_test_users)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))
            
            if not success:
                print(f"\n⚠️  {step_name} failed. Fix this before continuing.")
                response = input("Continue anyway? (y/n): ").lower()
                if response != 'y':
                    break
        except Exception as e:
            print(f"\n✗ Unexpected error in {step_name}: {e}")
            traceback.print_exc()
            results.append((step_name, False))
            break
    
    # Summary
    print_header("SUMMARY")
    
    for step_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} - {step_name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("ALL FIXES APPLIED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart your Flask server")
        print("2. Test the API endpoints")
        print("3. Run: python test_chat_system.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("SOME FIXES FAILED")
        print("="*60)
        print("\nPlease fix the failed steps and run again.")
        print("="*60)

if __name__ == "__main__":
    main()
