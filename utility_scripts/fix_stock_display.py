import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from app import app, db, Product
    
    print("=" * 80)
    print("FIXING STOCK DISPLAY - MAKING EVERYTHING SHOW PRODUCT.STOCK")
    print("=" * 80)
    
    with app.app_context():
        products = Product.query.filter_by(status='active').all()
        
        print(f"\nTotal Active Products: {len(products)}")
        print("\nCurrent Stock Values in Database:")
        print("-" * 80)
        
        for product in products:
            print(f"ID {product.id}: {product.name}")
            print(f"  Stock in DB: {product.stock}")
            print(f"  Price in DB: ₱{product.price:,.2f}")
        
        print("\n" + "=" * 80)
        print("WHAT NEEDS TO BE FIXED:")
        print("=" * 80)
        print("""
The database already has the correct stock values.
The issue is that the website and mobile app might be using
get_available_stock() which calculates differently.

We need to:
1. Make website show product.stock (not available_stock)
2. Make mobile app show product.stock (not available_stock)
3. Update API to return product.stock directly
""")
        
        print("\n" + "=" * 80)
        print("DATABASE VALUES (SOURCE OF TRUTH):")
        print("=" * 80)
        
        # Show first 5 products as examples
        for p in products[:5]:
            print(f"\nProduct ID {p.id}: {p.name}")
            print(f"  Price: ₱{p.price:,.2f}")
            print(f"  Stock: {p.stock}")
            print(f"  → Website should show: {p.stock}")
            print(f"  → Mobile app should show: {p.stock}")

except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure you run this from the kids/ directory")
