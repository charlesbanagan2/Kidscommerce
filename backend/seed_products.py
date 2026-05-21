"""
Seed script to populate sample products
Run this with: python seed_products.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

if not SUPABASE_DB_URL:
    print("❌ ERROR: SUPABASE_DB_URL not found in .env file")
    sys.exit(1)

# Sample products data
SAMPLE_PRODUCTS = [
    {
        'name': 'Baby Stroller - Lightweight',
        'description': 'Comfortable and easy-to-fold baby stroller perfect for travel',
        'price': 2999.00,
        'stock': 15,
        'status': 'approved',
        'category_id': 1,
        'seller_id': 1
    },
    {
        'name': 'Kids Educational Toy Set',
        'description': 'Interactive learning toys for children ages 3-6',
        'price': 899.00,
        'stock': 30,
        'status': 'approved',
        'category_id': 2,
        'seller_id': 1
    },
    {
        'name': 'Baby Feeding Bottle Set',
        'description': 'BPA-free feeding bottles with anti-colic design',
        'price': 499.00,
        'stock': 50,
        'status': 'approved',
        'category_id': 3,
        'seller_id': 1
    },
    {
        'name': 'Kids Backpack - Cartoon Design',
        'description': 'Durable and colorful backpack for school or travel',
        'price': 599.00,
        'stock': 25,
        'status': 'approved',
        'category_id': 4,
        'seller_id': 1
    },
    {
        'name': 'Baby Safety Gate',
        'description': 'Adjustable safety gate for stairs and doorways',
        'price': 1299.00,
        'stock': 10,
        'status': 'approved',
        'category_id': 5,
        'seller_id': 1
    }
]

try:
    engine = create_engine(SUPABASE_DB_URL)
    print("✓ Connected to database")
    
    with engine.connect() as conn:
        # Check if we need to create a default seller user
        result = conn.execute(text("SELECT COUNT(*) FROM \"user\" WHERE role = 'seller'"))
        seller_count = result.scalar()
        
        if seller_count == 0:
            print("⚠️  No seller users found. Creating default seller...")
            conn.execute(text("""
                INSERT INTO "user" (first_name, last_name, email, password, phone, address, role, status, created_at)
                VALUES ('Demo', 'Seller', 'seller@demo.com', 'password123', '09123456789', 'Manila, Philippines', 'seller', 'active', NOW())
                ON CONFLICT (email) DO NOTHING
            """))
            conn.commit()
            print("✓ Default seller created")
        
        # Check if categories exist
        result = conn.execute(text("SELECT COUNT(*) FROM category"))
        category_count = result.scalar()
        
        if category_count == 0:
            print("⚠️  No categories found. Creating default categories...")
            categories = [
                ('Baby Gear', 'Strollers, car seats, and baby carriers'),
                ('Toys', 'Educational and fun toys for kids'),
                ('Feeding', 'Bottles, utensils, and feeding accessories'),
                ('Clothing', 'Kids and baby clothing'),
                ('Safety', 'Safety gates, monitors, and protective gear')
            ]
            for name, desc in categories:
                conn.execute(text("""
                    INSERT INTO category (name, description, status, created_at)
                    VALUES (:name, :desc, 'active', NOW())
                """), {'name': name, 'desc': desc})
            conn.commit()
            print(f"✓ Created {len(categories)} categories")
        
        # Check existing products
        result = conn.execute(text("SELECT COUNT(*) FROM product WHERE status IN ('approved', 'active')"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print(f"\nℹ️  Found {existing_count} approved/active products already")
            response = input("Do you want to add more sample products? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                sys.exit(0)
        
        # Insert sample products
        print(f"\n📦 Adding {len(SAMPLE_PRODUCTS)} sample products...")
        for product in SAMPLE_PRODUCTS:
            conn.execute(text("""
                INSERT INTO product (name, description, price, stock, status, category_id, seller_id, created_at, reserved_stock, rating, review_count)
                VALUES (:name, :description, :price, :stock, :status, :category_id, :seller_id, NOW(), 0, 0.0, 0)
            """), product)
            print(f"   ✓ Added: {product['name']}")
        
        conn.commit()
        print(f"\n✅ Successfully added {len(SAMPLE_PRODUCTS)} products!")
        print("\n🎉 Your homepage should now display products.")
        print("   Restart your Flask app to see the changes.")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure your database connection is working")
    print("2. Check that tables exist (run migrations if needed)")
    print("3. Verify RLS policies allow inserts")
    sys.exit(1)
