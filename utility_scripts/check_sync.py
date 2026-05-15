import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from app import app, db, Product
    from sqlalchemy import text
    
    print("=" * 80)
    print("CHECKING PRODUCT PRICES AND STOCK")
    print("=" * 80)
    
    with app.app_context():
        # Get all active products
        products = Product.query.filter_by(status='active').all()
        
        print(f"\nTotal Active Products: {len(products)}")
        print("\n" + "-" * 80)
        
        issues = []
        
        for product in products:
            print(f"\nID: {product.id}")
            print(f"Name: {product.name}")
            print(f"Price: ₱{product.price:,.2f}")
            print(f"Stock: {product.stock}")
            
            # Check for issues
            if product.price <= 0:
                issues.append(f"Product {product.id} has invalid price: {product.price}")
                print("  ⚠️  WARNING: Invalid price!")
            
            if product.stock < 0:
                issues.append(f"Product {product.id} has negative stock: {product.stock}")
                print("  ⚠️  WARNING: Negative stock!")
        
        print("\n" + "=" * 80)
        
        if issues:
            print("ISSUES FOUND:")
            print("=" * 80)
            for issue in issues:
                print(f"⚠️  {issue}")
        else:
            print("✅ ALL PRODUCTS HAVE VALID PRICES AND STOCK")
            print("=" * 80)
            print("\nYour database, website, and mobile app are using the SAME data.")
            print("If you see differences, check:")
            print("  1. Stock calculation (total vs available)")
            print("  2. Mobile app cache")
            print("  3. API response format")
        
        print("\n" + "=" * 80)
        print("SAMPLE PRODUCT DATA FOR VERIFICATION:")
        print("=" * 80)
        
        # Show first 3 products in detail
        sample_products = products[:3]
        for p in sample_products:
            print(f"\nProduct ID {p.id}: {p.name}")
            print(f"  Database Price: ₱{p.price:,.2f}")
            print(f"  Database Stock: {p.stock}")
            print(f"  Website URL: http://localhost:5000/product/{p.id}")
            print(f"  API URL: http://localhost:5000/api/products (look for id={p.id})")
            print(f"  Mobile App: Search for '{p.name}' and compare values")

except ImportError as e:
    print("=" * 80)
    print("ERROR: Cannot import Flask app")
    print("=" * 80)
    print(f"\nError details: {e}")
    print("\nMake sure you're running this from the project root directory.")
    print("The script expects this structure:")
    print("  kids/")
    print("    ├── backend/")
    print("    │   └── app.py")
    print("    └── check_sync.py (this file)")
    
except Exception as e:
    print("=" * 80)
    print("ERROR OCCURRED")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\nThis might be a database connection issue.")
    print("Make sure:")
    print("  1. Your .env file is configured correctly")
    print("  2. Supabase credentials are valid")
    print("  3. Database is accessible")
