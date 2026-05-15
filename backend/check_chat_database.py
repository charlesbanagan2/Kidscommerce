"""
Database Check Script for Chat System
Verifies chat_message table exists and shows test data
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_chat_table():
    """Check if chat_message table exists"""
    print_header("Checking Chat Message Table")
    
    with app.app_context():
        try:
            # Try to import ChatMessage
            from unified_chat_api import register_unified_chat_api
            
            # This will create the table if it doesn't exist
            print("✓ ChatMessage model loaded")
            
            # Check if table exists by querying it
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_message'"
            ))
            
            if result.fetchone():
                print("✓ chat_message table exists in database")
                
                # Get table info
                result = db.session.execute(db.text("PRAGMA table_info(chat_message)"))
                columns = result.fetchall()
                
                print("\nTable Columns:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Count messages
                result = db.session.execute(db.text("SELECT COUNT(*) FROM chat_message"))
                count = result.fetchone()[0]
                print(f"\nTotal messages in database: {count}")
                
                return True
            else:
                print("✗ chat_message table does not exist")
                print("  Run: db.create_all() to create it")
                return False
                
        except Exception as e:
            print(f"✗ Error checking table: {e}")
            return False

def show_test_users():
    """Show available test users"""
    print_header("Available Test Users")
    
    with app.app_context():
        try:
            # Get buyers
            buyers = User.query.filter_by(role='buyer', status='active').limit(3).all()
            print("BUYERS:")
            for user in buyers:
                print(f"  ID: {user.id} | {user.first_name} {user.last_name} | {user.email}")
            
            # Get sellers
            sellers = User.query.filter_by(role='seller', status='active').limit(3).all()
            print("\nSELLERS:")
            for user in sellers:
                print(f"  ID: {user.id} | {user.first_name} {user.last_name} | {user.email}")
            
            # Get riders
            riders = User.query.filter_by(role='rider', status='active').limit(3).all()
            print("\nRIDERS:")
            for user in riders:
                print(f"  ID: {user.id} | {user.first_name} {user.last_name} | {user.email}")
            
            if not buyers:
                print("\n⚠️  No active buyers found. Create test accounts first.")
            if not sellers:
                print("⚠️  No active sellers found. Create test accounts first.")
            if not riders:
                print("⚠️  No active riders found. Create test accounts first.")
                
        except Exception as e:
            print(f"✗ Error fetching users: {e}")

def show_test_products():
    """Show available test products"""
    print_header("Available Test Products")
    
    with app.app_context():
        try:
            products = Product.query.filter_by(status='active').limit(5).all()
            
            if products:
                print("PRODUCTS:")
                for product in products:
                    seller = User.query.get(product.seller_id)
                    seller_name = f"{seller.first_name} {seller.last_name}" if seller else "Unknown"
                    print(f"  ID: {product.id} | {product.name} | ₱{product.price} | Seller: {seller_name}")
            else:
                print("⚠️  No active products found. Create test products first.")
                
        except Exception as e:
            print(f"✗ Error fetching products: {e}")

def show_recent_messages():
    """Show recent chat messages"""
    print_header("Recent Chat Messages")
    
    with app.app_context():
        try:
            result = db.session.execute(db.text("""
                SELECT 
                    cm.id,
                    cm.sender_id,
                    cm.receiver_id,
                    cm.message,
                    cm.product_id,
                    cm.is_read,
                    cm.created_at,
                    u1.first_name || ' ' || u1.last_name as sender_name,
                    u2.first_name || ' ' || u2.last_name as receiver_name
                FROM chat_message cm
                LEFT JOIN user u1 ON cm.sender_id = u1.id
                LEFT JOIN user u2 ON cm.receiver_id = u2.id
                ORDER BY cm.created_at DESC
                LIMIT 10
            """))
            
            messages = result.fetchall()
            
            if messages:
                print(f"Last {len(messages)} messages:\n")
                for msg in messages:
                    msg_id, sender_id, receiver_id, message, product_id, is_read, created_at, sender_name, receiver_name = msg
                    
                    read_status = "✓ Read" if is_read else "○ Unread"
                    product_info = f" [Product #{product_id}]" if product_id else ""
                    
                    print(f"[{msg_id}] {sender_name} → {receiver_name} {read_status}{product_info}")
                    print(f"     {message[:80]}...")
                    print(f"     {created_at}\n")
            else:
                print("No messages found in database.")
                print("Run test_chat_system.py to create test messages.")
                
        except Exception as e:
            print(f"✗ Error fetching messages: {e}")

def create_test_data():
    """Create minimal test data for testing"""
    print_header("Creating Test Data")
    
    with app.app_context():
        try:
            # Check if test users exist
            buyer = User.query.filter_by(email='testbuyer@gmail.com').first()
            seller = User.query.filter_by(email='testseller@gmail.com').first()
            rider = User.query.filter_by(email='testrider@gmail.com').first()
            
            created = []
            
            # Create test buyer if not exists
            if not buyer:
                buyer = User(
                    email='testbuyer@gmail.com',
                    password='Buyer123!',
                    first_name='Test',
                    last_name='Buyer',
                    phone='09123456789',
                    address='Test Address',
                    role='buyer',
                    status='active',
                    email_verified=True
                )
                db.session.add(buyer)
                created.append('Buyer')
            
            # Create test seller if not exists
            if not seller:
                seller = User(
                    email='testseller@gmail.com',
                    password='Seller123!',
                    first_name='Test',
                    last_name='Seller',
                    phone='09123456790',
                    address='Test Address',
                    role='seller',
                    status='active',
                    email_verified=True
                )
                db.session.add(seller)
                created.append('Seller')
            
            # Create test rider if not exists
            if not rider:
                rider = User(
                    email='testrider@gmail.com',
                    password='Rider123!',
                    first_name='Test',
                    last_name='Rider',
                    phone='09123456791',
                    address='Test Address',
                    role='rider',
                    status='active',
                    email_verified=True
                )
                db.session.add(rider)
                created.append('Rider')
            
            db.session.commit()
            
            if created:
                print(f"✓ Created test users: {', '.join(created)}")
                print("\nTest Credentials:")
                print("  Buyer:  testbuyer@gmail.com / Buyer123!")
                print("  Seller: testseller@gmail.com / Seller123!")
                print("  Rider:  testrider@gmail.com / Rider123!")
            else:
                print("✓ Test users already exist")
            
            # Create test product if seller exists and no products
            if seller:
                product = Product.query.filter_by(seller_id=seller.id).first()
                if not product:
                    from app import Category
                    
                    # Get or create category
                    category = Category.query.first()
                    if not category:
                        category = Category(name='Test Category', status='active')
                        db.session.add(category)
                        db.session.commit()
                    
                    product = Product(
                        name='Test Product',
                        description='This is a test product for chat testing',
                        price=999.00,
                        stock=10,
                        category_id=category.id,
                        seller_id=seller.id,
                        status='active'
                    )
                    db.session.add(product)
                    db.session.commit()
                    print(f"✓ Created test product (ID: {product.id})")
                else:
                    print(f"✓ Test product already exists (ID: {product.id})")
            
            print("\n✓ Test data ready!")
            print("\nUpdate test_chat_system.py with these values:")
            print(f"  TEST_PRODUCT_ID = {product.id if product else 1}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating test data: {e}")

def main():
    """Main function"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          CHAT SYSTEM DATABASE CHECK                        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check chat table
    table_exists = check_chat_table()
    
    # Show test users
    show_test_users()
    
    # Show test products
    show_test_products()
    
    # Show recent messages
    if table_exists:
        show_recent_messages()
    
    # Ask if user wants to create test data
    print("\n" + "="*60)
    response = input("\nCreate test data? (y/n): ").lower()
    if response == 'y':
        create_test_data()
    
    print("\n" + "="*60)
    print("Database check complete!")
    print("\nNext steps:")
    print("1. Update test_chat_system.py with user credentials and product ID")
    print("2. Run: python test_chat_system.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
