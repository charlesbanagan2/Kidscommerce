#!/usr/bin/env python3
"""
Check products from the Flask backend API
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

print("=" * 80)
print("CHECKING PRODUCTS FROM BACKEND API")
print("=" * 80)

try:
    # Fetch products list
    print("\n1. Fetching products list...")
    response = requests.get(f'{BASE_URL}/api/v1/products', timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if data.get('success') and data.get('products'):
        products = data['products']
        print(f"\n✓ Found {len(products)} products\n")
        
        for i, product in enumerate(products[:5], 1):
            print(f"\n{i}. {product.get('name', 'Unknown')}")
            print(f"   ID: {product.get('id')}")
            print(f"   Price: ${product.get('price', 0):.2f}")
            print(f"   Stock: {product.get('stock', 0)}")
            print(f"   Rating: {product.get('rating', 0)} ({product.get('review_count', 0)} reviews)")
            print(f"   Seller ID: {product.get('seller_id')}")
            
            # Check if seller info is included
            seller = product.get('seller', {})
            if isinstance(seller, dict):
                print(f"   Store Name: {seller.get('store_name', 'N/A')}")
                print(f"   Seller: {seller.get('name', 'N/A')}")
            
            # Check images
            gallery = product.get('gallery', [])
            image = product.get('image', '')
            print(f"   Main Image: {image}")
            if gallery:
                print(f"   Gallery Images: {len(gallery)} images")
                for j, img in enumerate(gallery[:3], 1):
                    print(f"      {j}. {img}")
            
            print(f"   Reviews: {product.get('review_count', 0)}")
    
    # Look for SpongeBob product
    print("\n" + "=" * 80)
    print("2. Looking for SpongeBob SquarePants Sticky Catcher...")
    
    for product in products:
        if 'SpongeBob' in product.get('name', '') or 'Sticky Catcher' in product.get('name', ''):
            product_id = product.get('id')
            print(f"\n✓ Found: {product.get('name')}")
            print(f"  Product ID: {product_id}")
            
            # Fetch detailed product info
            detail_response = requests.get(f'{BASE_URL}/api/v1/products/{product_id}', timeout=10)
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            
            if detail_data.get('success'):
                product_detail = detail_data['product']
                print(f"\n  DETAILED INFORMATION:")
                print(f"    Name: {product_detail.get('name')}")
                print(f"    Price: ${product_detail.get('price', 0):.2f}")
                print(f"    Stock: {product_detail.get('stock', 0)}")
                print(f"    Rating: {product_detail.get('rating', 0)}")
                print(f"    Review Count: {product_detail.get('review_count', 0)}")
                
                # Seller info
                seller = product_detail.get('seller', {})
                print(f"\n  SELLER/STORE INFORMATION:")
                print(f"    Seller ID: {seller.get('id')}")
                print(f"    Seller Name: {seller.get('name')}")
                print(f"    Store Name: {seller.get('store_name')}")
                print(f"    Store Logo: {seller.get('store_logo')}")
                
                # Reviews
                reviews = product_detail.get('reviews', [])
                print(f"\n  REVIEWS ({len(reviews)}):")
                if reviews:
                    for review in reviews:
                        print(f"    - Rating: {review.get('rating')}/5")
                        print(f"      Title: {review.get('title')}")
                        print(f"      Content: {review.get('content', 'No content')[:100]}...")
                        print(f"      By: {review.get('user_name')}")
                        print(f"      Date: {review.get('created_at')}")
                else:
                    print("    No reviews yet")
                
                # Gallery images
                gallery = product_detail.get('gallery', [])
                image = product_detail.get('image', '')
                print(f"\n  IMAGES:")
                print(f"    Main Image: {image}")
                if gallery:
                    print(f"    Gallery ({len(gallery)} images):")
                    for img in gallery:
                        print(f"      - {img}")
                else:
                    print(f"    No gallery images")

except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to backend at {BASE_URL}")
    print("  Make sure the Flask backend is running on http://localhost:5000")
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n" + "=" * 80)
