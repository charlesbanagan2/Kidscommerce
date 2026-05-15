import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import db, Product, get_available_stock
from sqlalchemy.orm import joinedload

print("Testing database and product data...\n")

# Get all active products
products = Product.query.filter_by(status='active').all()
print(f"Total active products: {len(products)}\n")

for p in products[:5]:  # Show first 5
    print(f"Product ID: {p.id}")
    print(f"  Name: {p.name}")
    print(f"  Stock: {p.stock}")
    print(f"  Image: {p.image_filename}")
    print(f"  Status: {p.status}")
    
    # Test get_available_stock
    try:
        avail = get_available_stock(p.id)
        print(f"  Available Stock (calculated): {avail}")
    except Exception as e:
        print(f"  Available Stock ERROR: {e}")
    
    print()

# Test loading one product with all relationships
print("\nTesting product detail load with relationships...")
try:
    product = Product.query.options(
        joinedload(Product.seller),
        joinedload(Product.category),
        joinedload(Product.reviews)
    ).filter_by(status='active').first()
    
    if product:
        print(f"Loaded: {product.name}")
        print(f"  Seller: {product.seller.first_name if product.seller else 'None'}")
        print(f"  Category: {product.category.name if product.category else 'None'}")
        print(f"  Reviews: {len(product.reviews)}")
        print(f"  Image: {product.image_filename}")
    else:
        print("No active products found!")
except Exception as e:
    print(f"ERROR loading product: {e}")
    import traceback
    traceback.print_exc()
