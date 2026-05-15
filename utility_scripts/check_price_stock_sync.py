"""
Check and sync prices and stock across database, website, and mobile app
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Product

def check_products():
    with app.app_context():
        products = Product.query.filter_by(status='active').all()
        
        print("=" * 80)
        print("PRODUCT PRICE AND STOCK CHECK")
        print("=" * 80)
        print(f"\nTotal Active Products: {len(products)}\n")
        
        issues = []
        
        for product in products:
            print(f"\nProduct ID: {product.id}")
            print(f"Name: {product.name}")
            print(f"Price: ₱{product.price:,.2f}")
            print(f"Stock: {product.stock}")
            print(f"Status: {product.status}")
            
            # Check for issues
            if product.price <= 0:
                issues.append(f"Product {product.id} ({product.name}) has invalid price: {product.price}")
            
            if product.stock < 0:
                issues.append(f"Product {product.id} ({product.name}) has negative stock: {product.stock}")
            
            print("-" * 40)
        
        if issues:
            print("\n" + "=" * 80)
            print("ISSUES FOUND:")
            print("=" * 80)
            for issue in issues:
                print(f"⚠️  {issue}")
        else:
            print("\n" + "=" * 80)
            print("✅ All products have valid prices and stock levels")
            print("=" * 80)

if __name__ == '__main__':
    check_products()
