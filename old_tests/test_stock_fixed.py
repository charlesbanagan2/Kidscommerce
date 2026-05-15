import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, db, Product
import os

with app.app_context():
    print("Testing product stock and images...\n")
    
    # Get first 5 active products
    products = Product.query.filter_by(status='active').limit(5).all()
    
    if not products:
        print("No active products found!")
    else:
        for p in products:
            print(f"Product ID: {p.id} - {p.name}")
            print(f"  Database stock: {p.stock}")
            
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
                print(f"  Gallery: {p.gallery[:100]}...")
            
            print()
    
    # Check for pending restock requests
    print("\nChecking for pending restock requests...")
    from app import get_data
    pending_restocks = get_data('restock_request', filters={'status': 'pending'})
    if pending_restocks:
        print(f"Found {len(pending_restocks)} pending restock requests:")
        for req in pending_restocks:
            print(f"  Product ID: {req.get('product_id')} - Status: {req.get('status')}")
    else:
        print("No pending restock requests")
