import requests
import json

# Try different passwords for buyer@gmail.com
backend_url = 'http://192.168.1.20:5000'
email = 'buyer@gmail.com'

passwords_to_try = [
    'password',
    'Buyer@1234',
    '123456',
    'buyer123',
    'test123',
    'buyer@123',
    'Password123',
]

print(f'Testing different passwords for {email}...\n')

for pwd in passwords_to_try:
    try:
        response = requests.post(
            f'{backend_url}/api/v1/auth/login',
            json={'email': email, 'password': pwd},
            timeout=5
        )
        
        status = '✅' if response.status_code == 200 else '❌'
        print(f'{status} Password "{pwd}": {response.status_code}')
        
        if response.status_code == 200:
            print(f'   SUCCESS! Response: {response.json()}')
            break
        
    except Exception as e:
        print(f'❌ Password "{pwd}": Error - {e}')
