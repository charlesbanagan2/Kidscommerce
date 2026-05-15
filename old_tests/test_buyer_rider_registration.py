#!/usr/bin/env python3
"""
Test buyer and rider registration
Verifies that users are registered with correct roles in the database
"""

import sys
import os
import json
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from sqlalchemy import text
import requests
import bcrypt

BASE_URL = 'http://192.168.1.20:5000'

def test_buyer_registration():
    """Test buyer registration through API"""
    print("\n" + "="*60)
    print("TEST 1: BUYER REGISTRATION")
    print("="*60)
    
    buyer_data = {
        'first_name': 'John',
        'last_name': 'Buyer',
        'email': 'john.buyer@test.com',
        'phone': '+1234567890',
        'password': 'password123',
        'role': 'buyer'
    }
    
    print(f"\nRegistering buyer:")
    print(f"  Email: {buyer_data['email']}")
    print(f"  Role: {buyer_data['role']}")
    print(f"  Name: {buyer_data['first_name']} {buyer_data['last_name']}")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/v1/auth/register',
            json=buyer_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            user = result.get('user', {})
            print(f"\n✅ BUYER REGISTRATION SUCCESSFUL")
            print(f"   User ID: {user.get('id')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Role: {user.get('role')}")
            return True, user.get('id')
        else:
            print(f"❌ REGISTRATION FAILED: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False, None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def test_rider_registration():
    """Test rider registration through API"""
    print("\n" + "="*60)
    print("TEST 2: RIDER REGISTRATION")
    print("="*60)
    
    rider_data = {
        'first_name': 'Jane',
        'last_name': 'Rider',
        'email': 'jane.rider@test.com',
        'phone': '+1987654321',
        'password': 'password123',
        'role': 'rider',
        'vehicle_type': 'motorcycle',
        'vehicle_number': 'ABC1234',
        'drivers_license': 'DL12345'
    }
    
    print(f"\nRegistering rider:")
    print(f"  Email: {rider_data['email']}")
    print(f"  Role: {rider_data['role']}")
    print(f"  Name: {rider_data['first_name']} {rider_data['last_name']}")
    print(f"  Vehicle: {rider_data['vehicle_type']} ({rider_data['vehicle_number']})")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/v1/auth/register',
            json=rider_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            user = result.get('user', {})
            print(f"\n✅ RIDER REGISTRATION SUCCESSFUL")
            print(f"   User ID: {user.get('id')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Role: {user.get('role')}")
            return True, user.get('id')
        else:
            print(f"❌ REGISTRATION FAILED: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False, None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def verify_buyer_in_database(user_id):
    """Verify buyer is stored correctly in database"""
    print("\n" + "="*60)
    print("TEST 3: VERIFY BUYER IN DATABASE")
    print("="*60)
    
    with app.app_context():
        result = db.session.execute(
            text("SELECT id, email, role, first_name, last_name, status FROM user WHERE id = :id"),
            {"id": user_id}
        )
        user = result.fetchone()
        
        if user:
            print(f"\n✅ BUYER FOUND IN DATABASE")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Role: {user[2]} {'✅ CORRECT' if user[2] == 'buyer' else '❌ WRONG'}")
            print(f"   Name: {user[3]} {user[4]}")
            print(f"   Status: {user[5]}")
            return user[2] == 'buyer'
        else:
            print(f"❌ BUYER NOT FOUND IN DATABASE")
            return False

def verify_rider_in_database(user_id):
    """Verify rider is stored correctly in database"""
    print("\n" + "="*60)
    print("TEST 4: VERIFY RIDER IN DATABASE")
    print("="*60)
    
    with app.app_context():
        result = db.session.execute(
            text("SELECT id, email, role, first_name, last_name, status FROM user WHERE id = :id"),
            {"id": user_id}
        )
        user = result.fetchone()
        
        if user:
            print(f"\n✅ RIDER FOUND IN DATABASE")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Role: {user[2]} {'✅ CORRECT' if user[2] == 'rider' else '❌ WRONG'}")
            print(f"   Name: {user[3]} {user[4]}")
            print(f"   Status: {user[5]}")
            return user[2] == 'rider'
        else:
            print(f"❌ RIDER NOT FOUND IN DATABASE")
            return False

def verify_all_users_have_roles():
    """Verify all users in database have proper roles"""
    print("\n" + "="*60)
    print("TEST 5: VERIFY ALL USERS HAVE ROLES")
    print("="*60)
    
    with app.app_context():
        result = db.session.execute(
            text("SELECT COUNT(*) as total, role FROM user GROUP BY role")
        )
        roles = result.fetchall()
        
        print(f"\nUser counts by role:")
        total = 0
        for count, role in roles:
            print(f"  {role.upper()}: {count} users")
            total += count
        
        print(f"\nTotal users: {total}")
        
        # Check for NULL roles
        null_result = db.session.execute(
            text("SELECT COUNT(*) FROM user WHERE role IS NULL OR role = ''")
        )
        null_count = null_result.scalar()
        
        if null_count == 0:
            print(f"✅ No users with NULL or empty roles")
            return True
        else:
            print(f"❌ Found {null_count} users with NULL or empty roles")
            return False

def test_invalid_role():
    """Test that invalid roles are rejected"""
    print("\n" + "="*60)
    print("TEST 6: VERIFY INVALID ROLES ARE REJECTED")
    print("="*60)
    
    invalid_data = {
        'first_name': 'Invalid',
        'last_name': 'User',
        'email': 'invalid.role@test.com',
        'phone': '+1111111111',
        'password': 'password123',
        'role': 'admin'  # Invalid role
    }
    
    print(f"\nAttempting registration with invalid role 'admin'...")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/v1/auth/register',
            json=invalid_data,
            timeout=10
        )
        
        if response.status_code == 400:
            error = response.json().get('error', '')
            if 'Invalid role' in error or 'buyer or rider' in error.lower():
                print(f"✅ CORRECTLY REJECTED INVALID ROLE")
                print(f"   Error: {error}")
                return True
        
        print(f"❌ INVALID ROLE WAS NOT PROPERLY REJECTED")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "BUYER AND RIDER REGISTRATION TEST SUITE")
    print("="*70)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Buyer registration
    tests_total += 1
    buyer_success, buyer_id = test_buyer_registration()
    if buyer_success:
        tests_passed += 1
    
    # Test 2: Rider registration
    tests_total += 1
    rider_success, rider_id = test_rider_registration()
    if rider_success:
        tests_passed += 1
    
    # Test 3: Verify buyer in database
    if buyer_success and buyer_id:
        tests_total += 1
        if verify_buyer_in_database(buyer_id):
            tests_passed += 1
    
    # Test 4: Verify rider in database
    if rider_success and rider_id:
        tests_total += 1
        if verify_rider_in_database(rider_id):
            tests_passed += 1
    
    # Test 5: Verify all users have roles
    tests_total += 1
    if verify_all_users_have_roles():
        tests_passed += 1
    
    # Test 6: Invalid role rejection
    tests_total += 1
    if test_invalid_role():
        tests_passed += 1
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED - Buyer and Rider registration working correctly!")
        print("\n✅ Key Findings:")
        print("   • Buyers are registered with role='buyer'")
        print("   • Riders are registered with role='rider'")
        print("   • All users stored in single 'user' table")
        print("   • Invalid roles properly rejected")
        print("   • Roles correctly persisted in database")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
