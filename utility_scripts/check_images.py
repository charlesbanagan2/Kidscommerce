import sys
import os
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, Product

with app.app_context():
    print("Checking product images on disk...\n")
    
    products = Product.query.filter_by(status='active').limit(5).all()
    
    upload_dir = r'C:\Users\mnban\Documents\kids\backend\static\uploads'
    
    for p in products:
        print(f"Product ID: {p.id} - {p.name}")
        print(f"  Stock: {p.stock}")
        print(f"  Image filename in DB: {p.image_filename}")
        
        if p.image_filename:
            # Try different path combinations
            paths_to_check = [
                os.path.join(upload_dir, p.image_filename),
                os.path.join(upload_dir, p.image_filename.replace('uploads/', '')),
                os.path.join(upload_dir, p.image_filename.replace('uploads\\', '')),
            ]
            
            found = False
            for path in paths_to_check:
                if os.path.exists(path):
                    print(f"  IMAGE FOUND: {path}")
                    found = True
                    break
            
            if not found:
                print(f"  IMAGE NOT FOUND - checked:")
                for path in paths_to_check:
                    print(f"    - {path}")
        else:
            print(f"  No image filename in database")
        
        print()
    
    # List what's actually in uploads folder
    print("\n" + "="*60)
    print("Files in uploads folder:")
    if os.path.exists(upload_dir):
        files = os.listdir(upload_dir)
        print(f"Total files: {len(files)}")
        for f in files[:20]:  # Show first 20
            print(f"  - {f}")
    else:
        print(f"Uploads folder not found: {upload_dir}")
