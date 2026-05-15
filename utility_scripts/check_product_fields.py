import requests
import json

backend_url = 'http://192.168.1.20:5000'

print('Checking product API response details...\n')

try:
    response = requests.get(
        f'{backend_url}/api/v1/products?per_page=1',
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('products'):
            product = data['products'][0]
            print(f'Product: {product.get("name")}\n')
            print('All fields:')
            for key, value in product.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f'  {key}: {value[:100]}...')
                else:
                    print(f'  {key}: {value}')
    
except Exception as e:
    print(f'Error: {e}')
