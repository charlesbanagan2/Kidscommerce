import requests
import json

backend_url = 'http://192.168.1.20:5000'

test_credentials = [
    ('Matt@gmail.com', '030904Jeff!', 'buyer'),
    ('rider@gmail.com', 'Rider@1234', 'rider'),
    ('admin@kidscommerce.com', 'admin123', 'admin'),
]

print('Testing login with known credentials...\n')

for email, password, role in test_credentials:
    try:
        response = requests.post(
            f'{backend_url}/api/v1/auth/login',
            json={'email': email, 'password': password},
            timeout=5
        )
        
        status = '✅' if response.status_code == 200 else '❌'
        print(f'{status} {email} ({role}): {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   User: {data.get("user", {}).get("email")}')
            print(f'   Role: {data.get("user", {}).get("role")}')
            print(f'   Token present: {"Yes" if data.get("token") else "No"}')
        else:
            print(f'   Error: {response.json().get("error", "Unknown error")}')
        print()
        
    except Exception as e:
        print(f'❌ {email}: Error - {e}\n')
