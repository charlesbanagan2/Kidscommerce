#!/usr/bin/env python
"""Test API login endpoint"""
import requests
import json

API_BASE_URL = 'http://192.168.1.20:5000'

def test_login():
    """Test login endpoint"""
    url = f'{API_BASE_URL}/api/v1/auth/login'
    payload = {
        'email': 'testbuyer@test.com',
        'password': 'test123'
    }
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Testing login endpoint: {url}")
        print(f"Payload: {json.dumps(payload)}")
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✓ Login successful!")
                print(f"  User: {data.get('user', {}).get('email')}")
                print(f"  Role: {data.get('user', {}).get('role')}")
                if 'tokens' in data:
                    print(f"  Access Token: {data['tokens'].get('access_token', '')[:20]}...")
                    print(f"  Refresh Token: {data['tokens'].get('refresh_token', '')[:20]}...")
            else:
                print("\n✗ Login failed")
                print(f"  Error: {data.get('error')}")
        else:
            print(f"\n✗ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")

if __name__ == '__main__':
    test_login()
