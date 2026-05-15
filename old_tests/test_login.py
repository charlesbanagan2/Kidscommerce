import requests
import json

# Try login with a known buyer account
email = 'buyer@gmail.com'
password = 'password'  # Try common password
backend_url = 'http://192.168.1.20:5000'

print(f'Testing login with {email}...')

try:
    response = requests.post(
        f'{backend_url}/api/v1/auth/login',
        json={'email': email, 'password': password},
        timeout=10
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        data = response.json()
        print('\n✅ Login successful!')
        print(json.dumps(data, indent=2))
    else:
        print(f'\n❌ Login failed with status {response.status_code}')
        
except Exception as e:
    print(f'Error: {e}')
