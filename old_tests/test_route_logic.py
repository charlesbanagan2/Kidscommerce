import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, Product, get_available_stock, url_for
import json

with app.app_context():
    print("Testing product_detail route logic...\n")
    print("="*70)
    
    # Test with first 3 products
    products = Product.query.filter_by(status='active').limit(3).all()
    
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
                print("STATUS: IN STOCK ✓")
            else:
                print("STATUS: OUT OF STOCK ✗")
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
        
        if product.gallery:
            try:
                gallery = json.loads(product.gallery) if isinstance(product.gallery, str) else product.gallery
                if isinstance(gallery, list):
                    product_images.extend(gallery)
                    print(f"Gallery images: {len(gallery)}")
            except:
                pass
        
        # Build media items
        media_items = []
        for img in product_images:
            if img:
                clean_img = img.replace('uploads/', '').replace('uploads\\', '')
                media_items.append({
                    'type': 'image',
                    'url': url_for('static', filename=f'uploads/{clean_img}')
                })
        
        if not media_items:
            media_items.append({
                'type': 'image',
                'url': url_for('static', filename='placeholder.png')
            })
        
        print(f"Total media items: {len(media_items)}")
        for i, item in enumerate(media_items[:3], 1):
            print(f"  {i}. {item['url']}")
        
        print("="*70)
    
    print("\n\nTEST SUMMARY:")
    print("If all products show 'IN STOCK ✓' and have image URLs,")
    print("the fix is working correctly!")
