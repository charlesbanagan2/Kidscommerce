import requests
import json

backend_url = 'http://192.168.1.20:5000'

print('Testing /api/v1/products endpoint...\n')

try:
    # Test without authentication
    response = requests.get(
        f'{backend_url}/api/v1/products',
        timeout=5
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'\nResponse:')
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if 'products' in data:
        print(f'\n✅ Products found: {len(data.get("products", []))}')
    else:
        print(f'\n⚠️ Response keys: {list(data.keys())}')
    
except Exception as e:
    print(f'Error: {e}')
