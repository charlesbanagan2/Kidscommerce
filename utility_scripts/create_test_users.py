#!/usr/bin/env python3
"""
Create test users for Flutter app testing
"""

import requests
import json

def create_test_users():
    base_url = 'http://192.168.1.20:5000/api/v1'
    
    print('Creating Test Users for Flutter App...')
    print('=' * 50)
    
    # Test users to create
    test_users = [
        {
            'email': 'buyer@test.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'Buyer',
            'phone': '+1234567890',
            'role': 'buyer'
        },
        {
            'email': 'rider@test.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'Rider',
            'phone': '+1234567891',
            'role': 'rider'
        }
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(f'{base_url}/auth/register', json=user_data, timeout=10)
            if response.status_code == 201:
                data = response.json()
                user = data.get('user', {})
                print(f'Created {user.get("role", "")}: {user.get("first_name", "")} {user.get("last_name", "")}')
                print(f'  Email: {user.get("email", "")}')
            elif response.status_code == 409:
                print(f'User {user_data["email"]} already exists')
            else:
                print(f'Failed to create {user_data["email"]}: {response.status_code}')
                print(f'Error: {response.text}')
        except Exception as e:
            print(f'Error creating {user_data["email"]}: {e}')
    
    print('=' * 50)
    print('Test users ready for Flutter app testing:')
    print('Buyer: buyer@test.com / password123')
    print('Rider: rider@test.com / password123')

if __name__ == '__main__':
    create_test_users()
