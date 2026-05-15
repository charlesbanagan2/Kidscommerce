#!/usr/bin/env python3
"""
Test script for Mobile API endpoints
Run this to verify API is working before Flutter development
"""

import requests
import json

def test_api():
    base_url = 'http://127.0.0.1:5000/api/v1'
    
    print('Testing Mobile API Endpoints...')
    print('=' * 50)
    
    # Test 1: Get categories (public endpoint)
    try:
        response = requests.get(f'{base_url}/categories')
        print(f'✓ GET /categories: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Found {len(data.get("categories", []))} categories')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'✗ GET /categories: Error - {e}')
    
    # Test 2: Get products (public endpoint)
    try:
        response = requests.get(f'{base_url}/products')
        print(f'✓ GET /products: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Found {len(data.get("products", []))} products')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'✗ GET /products: Error - {e}')
    
    # Test 3: Register test user
    try:
        test_user = {
            'email': 'testbuyer@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Buyer',
            'phone': '+1234567890',
            'role': 'buyer'
        }
        response = requests.post(f'{base_url}/auth/register', json=test_user)
        print(f'✓ POST /auth/register: {response.status_code}')
        if response.status_code == 201:
            print('  Test user created successfully')
        elif response.status_code == 409:
            print('  Test user already exists')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'✗ POST /auth/register: Error - {e}')
    
    # Test 4: Login test user
    try:
        login_data = {
            'email': 'testbuyer@example.com',
            'password': 'testpass123'
        }
        response = requests.post(f'{base_url}/auth/login', json=login_data)
        print(f'✓ POST /auth/login: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            token = data.get('tokens', {}).get('access_token')
            print('  Login successful, token received')
            
            # Test 5: Get user profile (protected endpoint)
            if token:
                headers = {'Authorization': f'Bearer {token}'}
                try:
                    response = requests.get(f'{base_url}/user/profile', headers=headers)
                    print(f'✓ GET /user/profile: {response.status_code}')
                    if response.status_code == 200:
                        user_data = response.json().get('user', {})
                        print(f'  User: {user_data.get("first_name", "")} {user_data.get("last_name", "")}')
                    else:
                        print(f'  Error: {response.text}')
                except Exception as e:
                    print(f'✗ GET /user/profile: Error - {e}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'✗ POST /auth/login: Error - {e}')
    
    print('=' * 50)
    print('API Testing Complete!')

if __name__ == '__main__':
    test_api()
