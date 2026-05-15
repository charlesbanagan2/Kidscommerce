#!/usr/bin/env python
import requests
import json

print("=" * 70)
print("TESTING STORE_BACKGROUND FIELD IN API RESPONSE")
print("=" * 70)

response = requests.get('http://192.168.1.20:5000/api/v1/products')
data = response.json()

if data.get('products'):
    product = data['products'][0]
    print('\nFirst Product Fields:')
    print(f'  - name: {product.get("name")}')
    print(f'  - seller_id: {product.get("seller_id")}')
    print(f'  - store_name: {product.get("store_name")}')
    print(f'  - store_logo: {product.get("store_logo")}')
    print(f'  - store_background: {product.get("store_background")}')
    print(f'  - store_background_url: {product.get("store_background_url")}')
    print()
    
    if product.get('store_background') or product.get('store_background_url'):
        print('✓ store_background field IS present in API response!')
    else:
        print('✗ store_background field is MISSING from API response')
        print('\nAvailable product keys:')
        for key in sorted(product.keys()):
            print(f'  - {key}')

print("\n" + "=" * 70)
