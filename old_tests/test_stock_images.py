import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import db, Product, get_available_stock
import os

print("Testing product stock and images...\n")

# Get first 5 active products
products = Product.query.filter_by(status='active').limit(5).all()

for p in products:
    print(f"Product ID: {p.id} - {p.name}")
    print(f"  Database stock: {p.stock}")
    
    # Test get_available_stock
    try:
        avail = get_available_stock(p.id)
        print(f"  Available stock (calculated): {avail}")
    except Exception as e:
        print(f"  ERROR calculating stock: {e}")
    
    # Check image
    print(f"  Image filename: {p.image_filename}")
    if p.image_filename:
        img_path = os.path.join(r'C:\Users\mnban\Documents\kids\backend\static\uploads', p.image_filename)
        exists = os.path.exists(img_path)
        print(f"  Image exists: {exists}")
        if not exists:
            print(f"  Looking for: {img_path}")
    
    # Check gallery
    if p.gallery:
        print(f"  Gallery: {p.gallery}")
    
    print()

# Test get_available_stock function directly
print("\nTesting get_available_stock function...")
try:
    test_product = Product.query.filter_by(status='active').first()
    if test_product:
        print(f"Testing with product ID {test_product.id}")
        print(f"Stock in DB: {test_product.stock}")
        result = get_available_stock(test_product.id)
        print(f"Function returned: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
