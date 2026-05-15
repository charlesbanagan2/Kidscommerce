#!/usr/bin/env python3
"""
Detailed Image Gallery Debug Report
Check database, API, and template rendering
"""

import sys
sys.path.insert(0, 'backend')

from app import app, db, Product, SellerApplication, Review
import json

print("=" * 100)
print("PRODUCT IMAGE GALLERY DEBUG REPORT")
print("=" * 100)

with app.app_context():
    all_products = Product.query.filter_by(status='active').limit(5).all()
    
    print(f"\n🔍 Checking {len(all_products)} products for image/gallery data\n")
    
    for idx, product in enumerate(all_products, 1):
        print(f"\n{'='*100}")
        print(f"PRODUCT #{idx}: {product.name}")
        print(f"{'='*100}")
        
        print(f"\n1️⃣  DATABASE STORAGE:")
        print(f"   Product ID: {product.id}")
        print(f"   Main Image (image_filename): {product.image_filename}")
        print(f"   Gallery (JSON): {product.gallery}")
        print(f"   Gallery Type: {type(product.gallery)}")
        
        if product.gallery:
            print(f"   Gallery Count: {len(product.gallery)}")
            if isinstance(product.gallery, (list, tuple)):
                for i, img in enumerate(product.gallery, 1):
                    print(f"      {i}. {img}")
            elif isinstance(product.gallery, str):
                print(f"   ⚠️  WARNING: Gallery is stored as STRING instead of JSON array!")
                try:
                    parsed = json.loads(product.gallery)
                    print(f"   Parsed as: {parsed}")
                except:
                    print(f"   Cannot parse as JSON")
        else:
            print(f"   ⚠️  No gallery images")
        
        if product.video_filename:
            print(f"   Video: {product.video_filename}")
        
        # Calculate what media_items would be
        print(f"\n2️⃣  WHAT MEDIA_ITEMS WOULD BE (for template):")
        media_items = []
        
        if product.image_filename:
            media_items.append({
                'type': 'image',
                'path': f'/static/uploads/{product.image_filename}'
            })
            print(f"   [1] Main image: /uploads/{product.image_filename}")
        
        if product.gallery:
            if isinstance(product.gallery, list):
                for i, fn in enumerate(product.gallery, 1):
                    media_items.append({
                        'type': 'image',
                        'path': f'/static/uploads/{fn}'
                    })
                    print(f"   [{len(media_items)}] Gallery: /uploads/{fn}")
            else:
                print(f"   ⚠️  Gallery not iterable (type: {type(product.gallery)})")
        
        if product.video_filename:
            media_items.append({
                'type': 'video',
                'path': f'/static/uploads/{product.video_filename}'
            })
            print(f"   [{len(media_items)}] Video: /uploads/{product.video_filename}")
        
        print(f"\n   Total Media Items: {len(media_items)}")
        
        # Check if files exist
        print(f"\n3️⃣  FILE EXISTENCE CHECK:")
        import os
        upload_dir = os.path.join('backend', 'static', 'uploads')
        
        if product.image_filename:
            main_path = os.path.join(upload_dir, product.image_filename)
            exists = os.path.exists(main_path)
            print(f"   Main: {product.image_filename} → {'✓ EXISTS' if exists else '✗ MISSING'}")
        
        if product.gallery and isinstance(product.gallery, list):
            for fn in product.gallery:
                path = os.path.join(upload_dir, fn)
                exists = os.path.exists(path)
                print(f"   Gallery: {fn} → {'✓ EXISTS' if exists else '✗ MISSING'}")
        
        print()

print("\n" + "=" * 100)
print("RECOMMENDATIONS")
print("=" * 100)
print("""
✓ If gallery shows "No gallery images":
  1. Check if gallery is NULL in database (it should be a JSON array)
  2. Re-upload the product images
  3. Check browser console for JS errors

✓ If gallery is stored as STRING instead of JSON:
  1. Need to fix how product.gallery is being stored
  2. It should be a Python list that gets auto-serialized to JSON

✓ If files are missing:
  1. Check if uploads folder has the files
  2. Check folder permissions
  3. Verify file paths in database are correct

✓ In the template:
  - media_items is passed from backend
  - Loop creates thumbnail buttons for each item
  - Clicking thumbnail should show image in main viewer
""")

print("\n" + "=" * 100)
