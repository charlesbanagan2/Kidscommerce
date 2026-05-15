import requests
import json

backend_url = 'http://192.168.1.20:5000'

email = 'Matt@gmail.com'
password = '030904Jeff!'

print(f'Testing login with {email}...\n')

try:
    response = requests.post(
        f'{backend_url}/api/v1/auth/login',
        json={'email': email, 'password': password},
        timeout=5
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'\nFull Response:')
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f'Error: {e}')
