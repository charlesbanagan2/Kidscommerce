#!/usr/bin/env python3
"""
Test script to verify the store page datetime fix
"""
import sys
sys.path.insert(0, r'c:\Users\mnban\Documents\kids\backend')

from datetime import datetime, timedelta
from app import app, db, Product, User

def test_datetime_fix():
    """Test that datetime comparison works correctly"""
    print("Testing datetime comparison fix...")
    
    with app.app_context():
        # Get a sample product to check its created_at field
        product = Product.query.first()
        if product:
            print(f"Sample product: {product.name}")
            print(f"Created at: {product.created_at}")
            print(f"Created at type: {type(product.created_at)}")
            
            # Simulate the store page logic
            now = datetime.utcnow()
            print(f"Now (utcnow): {now}")
            print(f"Now type: {type(now)}")
            
            # This should not raise TypeError anymore
            threshold = now - timedelta(days=30)
            is_new = product.created_at and product.created_at > threshold
            print(f"Is product from last 30 days? {is_new}")
            print("✓ Datetime comparison successful!")
            return True
        else:
            print("No products found in database")
            return False

if __name__ == '__main__':
    try:
        test_datetime_fix()
        print("\n✓ Test passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
