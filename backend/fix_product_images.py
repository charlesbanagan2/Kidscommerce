"""
Script to fix product images by assigning available images from uploads folder
to products that don't have images.
"""

import os
import sys
from app import app, db, Product

# Get list of available images in uploads folder
uploads_dir = 'static/uploads'
available_images = []

for filename in os.listdir(uploads_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
        # Skip directories and system files
        if os.path.isfile(os.path.join(uploads_dir, filename)):
            available_images.append(filename)

print(f"Found {len(available_images)} available images in uploads folder")

with app.app_context():
    # Get all products without images
    products_without_images = Product.query.filter(
        (Product.image_filename == None) | (Product.image_filename == '')
    ).all()
    
    print(f"Found {len(products_without_images)} products without images")
    
    # Assign images to products
    for i, product in enumerate(products_without_images):
        if i < len(available_images):
            product.image_filename = available_images[i]
            print(f"Assigned {available_images[i]} to product: {product.name}")
        else:
            # Use a default image if we run out
            product.image_filename = 'default-store-logo.png'
            print(f"Assigned default image to product: {product.name}")
    
    db.session.commit()
    print("Database updated successfully!")
