"""
Comprehensive Product and Store Information Report
This script will check all products in the system and display:
1. All products with their seller/store information
2. SpongeBob SquarePants Sticky Catcher details with reviews
3. Product images and gallery information
"""

import sys
sys.path.insert(0, 'backend')

from app import app, db, Product, SellerApplication, Review, User

print("=" * 100)
print("COMPREHENSIVE PRODUCT AND STORE INFORMATION REPORT")
print("=" * 100)

with app.app_context():
    # Get all active products
    all_products = Product.query.filter_by(status='active').all()
    
    print(f"\n📊 TOTAL ACTIVE PRODUCTS: {len(all_products)}")
    print("\n" + "=" * 100)
    print("ALL PRODUCTS WITH STORE INFORMATION")
    print("=" * 100)
    
    for idx, product in enumerate(all_products, 1):
        # Get seller application info
        seller = product.seller
        seller_app = SellerApplication.query.filter_by(user_id=product.seller_id, status='approved').first()
        
        # Get review count
        review_count = Review.query.filter_by(product_id=product.id, status='published').count()
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(product_id=product.id).scalar() or 0
        
        print(f"\n{idx}. {product.name}")
        print(f"   ID: {product.id}")
        print(f"   Price: ${product.price:.2f} | Stock: {product.stock}")
        print(f"   Rating: ⭐ {avg_rating:.1f} ({review_count} reviews)")
        print(f"   Category: {product.category.name if product.category else 'N/A'}")
        
        # Seller/Store info
        print(f"\n   👤 SELLER INFORMATION:")
        print(f"      Seller ID: {product.seller_id}")
        print(f"      Seller Name: {seller.first_name} {seller.last_name}")
        
        if seller_app:
            print(f"   🏪 STORE INFORMATION:")
            print(f"      Store Name: {seller_app.store_name}")
            print(f"      Store Description: {seller_app.store_description[:100]}..." if seller_app.store_description else "      Store Description: N/A")
            print(f"      Store Status: {seller_app.status}")
            print(f"      Store Logo: {seller_app.store_logo if seller_app.store_logo else 'N/A'}")
        else:
            print(f"   🏪 STORE INFORMATION: Not yet registered")
        
        # Images
        print(f"\n   🖼️  IMAGES:")
        print(f"      Main Image: {product.image_filename if product.image_filename else 'N/A'}")
        if product.gallery:
            print(f"      Gallery ({len(product.gallery)} images):")
            for i, img in enumerate(product.gallery, 1):
                print(f"         {i}. {img}")
        else:
            print(f"      Gallery: No additional images")
        
        # Reviews summary
        if review_count > 0:
            print(f"\n   💬 REVIEWS ({review_count}):")
            reviews = Review.query.filter_by(product_id=product.id, status='published').all()
            for review in reviews[:2]:  # Show first 2 reviews
                print(f"      • {review.user.first_name} {review.user.last_name}: {review.rating}⭐ - {review.title}")
                if review.content:
                    print(f"        \"{review.content[:80]}...\"")
        else:
            print(f"\n   💬 REVIEWS: No reviews yet")
        
        print()
    
    # Special check for SpongeBob product
    print("\n" + "=" * 100)
    print("SPECIAL REPORT: SPONGEBOB SQUAREPANTS STICKY CATCHER")
    print("=" * 100)
    
    spongebob = Product.query.filter(
        db.or_(
            Product.name.ilike('%SpongeBob%'),
            Product.name.ilike('%Sticky Catcher%')
        )
    ).first()
    
    if spongebob:
        seller = spongebob.seller
        seller_app = SellerApplication.query.filter_by(user_id=spongebob.seller_id, status='approved').first()
        reviews = Review.query.filter_by(product_id=spongebob.id, status='published').all()
        
        print(f"\n✓ FOUND: {spongebob.name}")
        print(f"\n  BASIC INFO:")
        print(f"    Product ID: {spongebob.id}")
        print(f"    Price: ${spongebob.price:.2f}")
        print(f"    Stock: {spongebob.stock} units")
        print(f"    Description: {spongebob.description[:150]}...")
        
        print(f"\n  SELLER/STORE:")
        print(f"    Seller: {seller.first_name} {seller.last_name}")
        if seller_app:
            print(f"    Store Name: {seller_app.store_name}")
            print(f"    Store Status: {seller_app.status}")
        else:
            print(f"    Store: Not registered")
        
        print(f"\n  IMAGES:")
        print(f"    Main Image: {spongebob.image_filename if spongebob.image_filename else 'N/A'}")
        if spongebob.gallery:
            print(f"    Gallery Images: {len(spongebob.gallery)}")
            for i, img in enumerate(spongebob.gallery, 1):
                print(f"      {i}. {img}")
        else:
            print(f"    No additional gallery images")
        
        print(f"\n  REVIEWS: {len(reviews)} review(s)")
        for review in reviews:
            print(f"\n    Review #{review.id}:")
            print(f"      Rating: {review.rating}/5 ⭐")
            print(f"      Title: {review.title}")
            print(f"      Content: {review.content}")
            print(f"      By: {review.user.first_name} {review.user.last_name}")
            print(f"      Date: {review.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      Verified Purchase: {'Yes' if review.verified_purchase else 'No'}")
    else:
        print("\n✗ SpongeBob SquarePants Sticky Catcher product not found!")
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    # Count stores
    registered_sellers = SellerApplication.query.filter_by(status='approved').count()
    print(f"\n✓ Total Active Products: {len(all_products)}")
    print(f"✓ Registered Sellers/Stores: {registered_sellers}")
    print(f"✓ Products with Images: {sum(1 for p in all_products if p.image_filename)}")
    print(f"✓ Products with Gallery: {sum(1 for p in all_products if p.gallery)}")
    print(f"✓ Products with Reviews: {len([p for p in all_products if Review.query.filter_by(product_id=p.id, status='published').count() > 0])}")

print("\n" + "=" * 100)
