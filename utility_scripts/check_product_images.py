#!/usr/bin/env python3
"""Check product images in database"""
import sys
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')

from app import app, db, Product

with app.app_context():
    products = Product.query.limit(5).all()
    print(f"\n=== Checking {len(products)} Products ===\n")
    for p in products:
        print(f"Product ID: {p.id}")
        print(f"  Name: {p.name}")
        print(f"  Image: {p.image_filename}")
        print(f"  Gallery: {p.gallery}")
        print()
