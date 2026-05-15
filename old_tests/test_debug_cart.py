#!/usr/bin/env python3
"""Debug Add to Cart error"""
import sys
import json

sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')

from app import app, db, User, Product, Cart, token_required, request, verify_token, jsonify

# Simulate the Add to Cart request manually
print("="*70)
print("DEBUGGING ADD TO CART ERROR")
print("="*70)

with app.app_context():
    # Get test data
    product = Product.query.get(24)
    buyer = User.query.filter_by(role='buyer').first()
    
    print(f"\n1. Test Data:")
    print(f"  - Product: {product.name if product else 'NOT FOUND'} (ID: 24)")
    print(f"  - Product status: {product.status if product else 'N/A'}")
    print(f"  - Buyer: {buyer.email if buyer else 'NOT FOUND'}")
    print(f"  - Buyer ID: {buyer.id if buyer else 'N/A'}")
    
    # Check if Cart table exists and is accessible
    print(f"\n2. Checking Cart model:")
    print(f"  - Cart model: {Cart}")
    print(f"  - Cart table name: {Cart.__tablename__}")
    
    # Try to create a cart item manually
    if product and buyer:
        print(f"\n3. Testing Cart creation manually:")
        try:
            existing_cart = Cart.query.filter_by(
                user_id=buyer.id,
                product_id=24
            ).first()
            
            if existing_cart:
                print(f"  - Found existing cart item: {existing_cart.id}")
                print(f"  - Current quantity: {existing_cart.quantity}")
                existing_cart.quantity += 1
            else:
                print(f"  - Creating new cart item...")
                cart_item = Cart(
                    user_id=buyer.id,
                    product_id=24,
                    quantity=1
                )
                db.session.add(cart_item)
                print(f"  - Cart item created: {cart_item}")
            
            db.session.commit()
            print(f"  ✓ Cart operation successful!")
            
            # Verify it was saved
            saved_item = Cart.query.filter_by(
                user_id=buyer.id,
                product_id=24
            ).first()
            print(f"  - Saved quantity: {saved_item.quantity if saved_item else 'NOT FOUND'}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

print("\n" + "="*70)
print("DEBUG COMPLETE")
print("="*70)
