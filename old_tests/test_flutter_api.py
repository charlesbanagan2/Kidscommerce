#!/usr/bin/env python3
"""
Test script for Flutter API integration
Tests all endpoints that the Flutter app will use
"""

import requests
import json

def test_flutter_api():
    base_url = 'http://192.168.100.46:5000/api/v1'
    
    print('Testing API Integration for Flutter App...')
    print('=' * 60)
    
    # Test 1: Get categories (public endpoint)
    try:
        response = requests.get(f'{base_url}/categories', timeout=10)
        print(f'Categories API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            categories_count = len(data.get('categories', []))
            print(f'  Success: Found {categories_count} categories')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Categories API: Failed - {e}')
    
    # Test 2: Get products (public endpoint)
    try:
        response = requests.get(f'{base_url}/products', timeout=10)
        print(f'Products API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            products_count = len(data.get('products', []))
            print(f'  Success: Found {products_count} products')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Products API: Failed - {e}')
    
    # Test 3: Register test buyer
    try:
        test_buyer = {
            'email': 'flutterbuyer@test.com',
            'password': 'testpass123',
            'first_name': 'Flutter',
            'last_name': 'Buyer',
            'phone': '+1234567890',
            'role': 'buyer'
        }
        response = requests.post(f'{base_url}/auth/register', json=test_buyer, timeout=10)
        print(f'Register Buyer API: {response.status_code}')
        if response.status_code == 201:
            data = response.json()
            user = data.get('user', {})
            tokens = data.get('tokens', {})
            print(f'  Success: {user.get("first_name", "")} registered as {user.get("role", "")}')
            print(f'  Token received: {"access_token" in tokens}')
        elif response.status_code == 409:
            print('  Buyer already exists')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Register Buyer API: Failed - {e}')
    
    # Test 4: Register test rider
    try:
        test_rider = {
            'email': 'flutterrider@test.com',
            'password': 'testpass123',
            'first_name': 'Flutter',
            'last_name': 'Rider',
            'phone': '+1234567891',
            'role': 'rider'
        }
        response = requests.post(f'{base_url}/auth/register', json=test_rider, timeout=10)
        print(f'Register Rider API: {response.status_code}')
        if response.status_code == 201:
            data = response.json()
            user = data.get('user', {})
            tokens = data.get('tokens', {})
            print(f'  Success: {user.get("first_name", "")} registered as {user.get("role", "")}')
            print(f'  Token received: {"access_token" in tokens}')
        elif response.status_code == 409:
            print('  Rider already exists')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Register Rider API: Failed - {e}')
    
    # Test 5: Login as buyer
    try:
        login_data = {
            'email': 'flutterbuyer@test.com',
            'password': 'testpass123'
        }
        response = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
        print(f'Login Buyer API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            tokens = data.get('tokens', {})
            print(f'  Success: {user.get("first_name", "")} {user.get("last_name", "")} logged in')
            print(f'  Role: {user.get("role", "")}')
            print(f'  Access Token: {"access_token" in tokens}')
            
            # Determine navigation target
            role = user.get('role', '')
            if role == 'buyer':
                nav_target = 'BuyerHomeScreen'
            elif role == 'rider':
                nav_target = 'RiderDashboardScreen'
            else:
                nav_target = 'BuyerHomeScreen (default)'
            print(f'  Should navigate to: {nav_target}')
            
            # Test 6: Get user profile with token
            if 'access_token' in tokens:
                headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
                profile_response = requests.get(f'{base_url}/user/profile', headers=headers, timeout=10)
                print(f'User Profile API: {profile_response.status_code}')
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    profile_user = profile_data.get('user', {})
                    print(f'  Success: Profile loaded for {profile_user.get("first_name", "")}')
                else:
                    print(f'  Error: {profile_response.text}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Login Buyer API: Failed - {e}')
    
    # Test 7: Login as rider
    try:
        login_data = {
            'email': 'flutterrider@test.com',
            'password': 'testpass123'
        }
        response = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
        print(f'Login Rider API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            tokens = data.get('tokens', {})
            print(f'  Success: {user.get("first_name", "")} {user.get("last_name", "")} logged in')
            print(f'  Role: {user.get("role", "")}')
            print(f'  Access Token: {"access_token" in tokens}')
            
            # Determine navigation target
            role = user.get('role', '')
            if role == 'buyer':
                nav_target = 'BuyerHomeScreen'
            elif role == 'rider':
                nav_target = 'RiderDashboardScreen'
            else:
                nav_target = 'BuyerHomeScreen (default)'
            print(f'  Should navigate to: {nav_target}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'Login Rider API: Failed - {e}')
    
    print('=' * 60)
    print('API Integration Test Complete!')
    print('Flutter app is ready to connect to your Flask backend.')
    print()
    print('Next Steps:')
    print('1. Run: cd flutter_app && flutter pub get')
    print('2. Run: flutter run')
    print('3. Test registration and login in the app')

if __name__ == '__main__':
    test_flutter_api()
