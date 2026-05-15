"""Test script to verify get_available_stock() is working correctly"""
import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

from app import app, db, Product, get_available_stock

with app.app_context():
    # Test a few products
    test_product_ids = [17, 24, 15, 1, 2, 3]
    
    print("=" * 80)
    print("TESTING get_available_stock() AFTER FIX")
    print("=" * 80)
    
    for pid in test_product_ids:
        product = db.session.get(Product, pid)
        if product:
            available = get_available_stock(pid)
            print(f"\nProduct {pid}: {product.name}")
            print(f"  Database Stock: {product.stock}")
            print(f"  Available Stock (calculated): {available}")
            print(f"  Status: {'OK' if available > 0 else 'PROBLEM - Shows 0 but has stock!'}")
        else:
            print(f"\nProduct {pid}: NOT FOUND")
    
    print("\nIf all products show available stock > 0, the fix is working!")
