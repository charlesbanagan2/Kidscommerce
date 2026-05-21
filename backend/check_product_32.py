#!/usr/bin/env python3
"""Check product ID 32 in database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_data_by_id
import json

# Check product 32 with app context
with app.app_context():
    product = get_data_by_id('product', 32)

    if product:
        print("Product ID 32 found:")
        print(json.dumps(product, indent=2, default=str))
        print(f"\nStatus: {product.get('status')}")
        print(f"Stock: {product.get('stock')}")
        print(f"Name: {product.get('name')}")
    else:
        print("Product ID 32 NOT FOUND in database")
