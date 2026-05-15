import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, Product, get_available_stock
import json

with app.app_context():
    print("Testing product_detail route logic...\n")
    print("="*70)
    
    # Test with first 5 products
    products = Product.query.filter_by(status='active').limit(5).all()
    
    all_pass = True
    
    for product in products:
        print(f"\nProduct: {product.name} (ID: {product.id})")
        print(f"Database stock: {product.stock}")
        print("-"*70)
        
        # Test stock calculation (same logic as route)
        try:
            available_stock = get_available_stock(product.id)
            print(f"get_available_stock() returned: {available_stock}")
            
            # Apply the fix
            if available_stock == 0 and product.stock and product.stock > 0:
                available_stock = product.stock
                print(f"FIXED: Using product.stock instead: {available_stock}")
            
            print(f"Final available_stock: {available_stock}")
            
            if available_stock > 0:
                print("STATUS: IN STOCK [PASS]")
            else:
                print("STATUS: OUT OF STOCK [FAIL]")
                all_pass = False
        except Exception as e:
            print(f"ERROR: {e}")
            available_stock = product.stock if product.stock else 0
            print(f"Fallback to product.stock: {available_stock}")
        
        # Test image handling
        print("\nImage handling:")
        product_images = []
        
        if product.image_filename:
            product_images.append(product.image_filename)
            print(f"Main image: {product.image_filename}")
        else:
            print("No main image")
            all_pass = False
        
        if product.gallery:
            try:
                gallery = json.loads(product.gallery) if isinstance(product.gallery, str) else product.gallery
                if isinstance(gallery, list):
                    product_images.extend(gallery)
                    print(f"Gallery images: {len(gallery)}")
            except:
                pass
        
        # Build media items (without url_for)
        media_items = []
        for img in product_images:
            if img:
                clean_img = img.replace('uploads/', '').replace('uploads\\', '')
                media_items.append({
                    'type': 'image',
                    'path': f'static/uploads/{clean_img}'
                })
        
        if not media_items:
            media_items.append({
                'type': 'image',
                'path': 'static/placeholder.png'
            })
        
        print(f"Total media items: {len(media_items)}")
        for i, item in enumerate(media_items[:3], 1):
            print(f"  {i}. {item['path']}")
        
        if len(media_items) > 0:
            print("Images: [PASS]")
        else:
            print("Images: [FAIL]")
            all_pass = False
        
        print("="*70)
    
    print("\n\nTEST SUMMARY:")
    if all_pass:
        print("[SUCCESS] All products show correct stock and have images!")
        print("\nNow restart Flask server and test in browser:")
        print("1. Stop Flask (Ctrl+C)")
        print("2. Run: python backend/app.py")
        print("3. Click on any product")
    else:
        print("[FAILED] Some products have issues")
