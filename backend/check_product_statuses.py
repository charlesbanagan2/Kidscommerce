#!/usr/bin/env python3
"""Check product statuses in database"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, supabase
import json

with app.app_context():
    # Get all unique statuses
    products = supabase.table('product').select('id, name, status').limit(50).execute()
    
    statuses = {}
    for p in products.data:
        status = p['status']
        if status not in statuses:
            statuses[status] = []
        statuses[status].append({'id': p['id'], 'name': p['name'][:40]})
    
    print("Product Statuses Found:")
    print("=" * 60)
    for status, items in statuses.items():
        print(f"\n{status.upper()}: {len(items)} products")
        for item in items[:3]:  # Show first 3
            print(f"  - ID {item['id']}: {item['name']}")
