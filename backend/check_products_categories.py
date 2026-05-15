"""
Quick check for products and categories in the database
"""
import os
import sys
from app import app, db, Product, Category, Subcategory

with app.app_context():
    print("=" * 80)
    print("CHECKING PRODUCTS AND CATEGORIES")
    print("=" * 80)
    
    # Count categories
    category_count = Category.query.count()
    print(f"\nTotal Categories: {category_count}")
    
    if category_count > 0:
        print("\nCategories:")
        for cat in Category.query.limit(10).all():
            print(f"  - ID: {cat.id}, Name: {cat.name}, Status: {cat.status}")
    
    # Count subcategories
    subcategory_count = Subcategory.query.count()
    print(f"\nTotal Subcategories: {subcategory_count}")
    
    if subcategory_count > 0:
        print("\nSubcategories:")
        for sub in Subcategory.query.limit(10).all():
            print(f"  - ID: {sub.id}, Name: {sub.name}, Category ID: {sub.category_id}")
    
    # Count products
    product_count = Product.query.count()
    print(f"\nTotal Products: {product_count}")
    
    if product_count > 0:
        print("\nProducts:")
        for prod in Product.query.limit(10).all():
            print(f"  - ID: {prod.id}, Name: {prod.name}, Status: {prod.status}, Stock: {prod.stock}")
    
    # Count active products
    active_product_count = Product.query.filter_by(status='active').count()
    print(f"\nActive Products: {active_product_count}")
    
    if active_product_count > 0:
        print("\nActive Products:")
        for prod in Product.query.filter_by(status='active').limit(10).all():
            print(f"  - ID: {prod.id}, Name: {prod.name}, Price: {prod.price}")
    
    print("\n" + "=" * 80)
