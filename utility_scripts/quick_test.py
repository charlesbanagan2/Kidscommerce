#!/usr/bin/env python3
import requests

# Test basic API connectivity
base_url = 'http://192.168.100.46:5000/api/v1'

try:
    response = requests.get(f'{base_url}/categories', timeout=5)
    print(f'API Status: {response.status_code}')
    if response.status_code == 200:
        print('Flask backend is running and ready for Flutter app!')
    else:
        print('Backend issue detected')
except:
    print('Cannot connect to Flask backend')
