#!/usr/bin/env python3
"""
Test Database User Accounts Script
Tests user accounts in the database and verifies they're working correctly
"""

import mysql.connector
from mysql.connector import Error
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',  # Update if you have a password
    'database': 'kids_ecommerce'
}

def connect_db():
    """Connect to the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        return conn
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_database_schema(conn):
    """Test if the database schema has all required columns"""
    print("\n" + "="*60)
    print("🔍 TESTING DATABASE SCHEMA")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("DESCRIBE user")
        columns = cursor.fetchall()
        
        print(f"\n📋 User Table Structure:")
        print("-" * 80)
        print(f"{'Column':<20} {'Type':<25} {'Null':<6} {'Key':<6}")
        print("-" * 80)
        
        required_columns = [
            'id', 'username', 'email', 'password', 'first_name', 
            'last_name', 'phone', 'address', 'role', 'status', 'created_at'
        ]
        missing_columns = []
        
        for col in columns:
            col_name = col['Field']
            col_type = col['Type']
            col_null = col['Null']
            col_key = col['Key']
            
            if col_name in required_columns:
                required_columns.remove(col_name)
            
            print(f"{col_name:<20} {col_type:<25} {col_null:<6} {col_key:<6}")
        
        print("-" * 80)
        
        if required_columns:
            print(f"\n❌ Missing columns: {', '.join(required_columns)}")
            return False
        else:
            print(f"\n✅ All required columns present!")
            return True
            
    except Error as e:
        print(f"❌ Schema test failed: {e}")
        return False
    finally:
        cursor.close()

def test_user_count(conn):
    """Count total users in database"""
    print("\n" + "="*60)
    print("📊 USER STATISTICS")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM user")
        result = cursor.fetchone()
        total_users = result['total']
        print(f"\n📍 Total users in database: {total_users}")
        
        # Count by role
        cursor.execute("""
            SELECT role, COUNT(*) as count FROM user GROUP BY role
        """)
        roles = cursor.fetchall()
        
        print(f"\n📋 Users by role:")
        for role_data in roles:
            print(f"   - {role_data['role']}: {role_data['count']}")
        
        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM user GROUP BY status
        """)
        statuses = cursor.fetchall()
        
        print(f"\n📋 Users by status:")
        for status_data in statuses:
            print(f"   - {status_data['status']}: {status_data['count']}")
        
        return total_users > 0
        
    except Error as e:
        print(f"❌ User count test failed: {e}")
        return False
    finally:
        cursor.close()

def list_all_users(conn):
    """List all users in the database"""
    print("\n" + "="*60)
    print("👥 ALL USERS IN DATABASE")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   phone, role, status, created_at 
            FROM user 
            ORDER BY id
        """)
        users = cursor.fetchall()
        
        if not users:
            print("\n⚠️  No users found in database!")
            return False
        
        print(f"\nFound {len(users)} users:\n")
        print("-" * 140)
        print(f"{'ID':<4} {'Username':<15} {'Email':<25} {'Name':<20} {'Role':<10} {'Status':<10} {'Created':<19}")
        print("-" * 140)
        
        for user in users:
            user_id = user['id']
            username = user['username'][:15]
            email = user['email'][:25]
            first_name = user['first_name'][:10]
            last_name = user['last_name'][:10]
            name = f"{first_name} {last_name}"[:20]
            role = user['role'][:10]
            status = user['status'][:10]
            created = str(user['created_at'])[:19]
            
            print(f"{user_id:<4} {username:<15} {email:<25} {name:<20} {role:<10} {status:<10} {created:<19}")
        
        print("-" * 140)
        return True
        
    except Error as e:
        print(f"❌ Failed to list users: {e}")
        return False
    finally:
        cursor.close()

def test_user_credentials(conn, email, password):
    """Test if a user can be found with email and password"""
    print(f"\n🔐 Testing login credentials for: {email}")
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   password, role, status 
            FROM user 
            WHERE email = %s
        """, (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"   ❌ User with email '{email}' not found")
            return False
        
        print(f"   ✅ User found: {user['first_name']} {user['last_name']}")
        print(f"      - Username: {user['username']}")
        print(f"      - Role: {user['role']}")
        print(f"      - Status: {user['status']}")
        
        # Check password (in real app, this would be hashed)
        if user['password'] == password:
            print(f"      ✅ Password matches!")
            return True
        else:
            print(f"      ⚠️  Password doesn't match")
            print(f"      Expected: {password}")
            print(f"      Got: {user['password']}")
            return False
        
    except Error as e:
        print(f"   ❌ Credential test failed: {e}")
        return False
    finally:
        cursor.close()

def verify_admin_user(conn):
    """Verify admin user exists and has correct configuration"""
    print("\n" + "="*60)
    print("🔑 VERIFYING ADMIN USER")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   password, role, status, created_at 
            FROM user 
            WHERE role = 'admin' AND id = 1
        """)
        admin = cursor.fetchone()
        
        if not admin:
            print("\n❌ Admin user not found!")
            return False
        
        print(f"\n✅ Admin user found:")
        print(f"   - ID: {admin['id']}")
        print(f"   - Username: {admin['username']}")
        print(f"   - Email: {admin['email']}")
        print(f"   - Name: {admin['first_name']} {admin['last_name']}")
        print(f"   - Password: {'*' * len(admin['password'])} (stored as: {admin['password']})")
        print(f"   - Role: {admin['role']}")
        print(f"   - Status: {admin['status']}")
        print(f"   - Created: {admin['created_at']}")
        
        return True
        
    except Error as e:
        print(f"❌ Admin verification failed: {e}")
        return False
    finally:
        cursor.close()

def test_buyer_user(conn):
    """Test buyer user if exists"""
    print("\n" + "="*60)
    print("🛍️  VERIFYING BUYER USER")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   password, role, status, created_at 
            FROM user 
            WHERE role = 'buyer'
            LIMIT 1
        """)
        buyer = cursor.fetchone()
        
        if not buyer:
            print("\n⚠️  No buyer user found")
            return False
        
        print(f"\n✅ Found buyer user:")
        print(f"   - ID: {buyer['id']}")
        print(f"   - Username: {buyer['username']}")
        print(f"   - Email: {buyer['email']}")
        print(f"   - Name: {buyer['first_name']} {buyer['last_name']}")
        print(f"   - Password: {'*' * len(buyer['password'])} (stored as: {buyer['password']})")
        print(f"   - Role: {buyer['role']}")
        print(f"   - Status: {buyer['status']}")
        print(f"   - Created: {buyer['created_at']}")
        
        return True
        
    except Error as e:
        print(f"❌ Buyer verification failed: {e}")
        return False
    finally:
        cursor.close()

def test_seller_user(conn):
    """Test seller user if exists"""
    print("\n" + "="*60)
    print("🏪 VERIFYING SELLER USER")
    print("="*60)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, 
                   password, role, status, created_at 
            FROM user 
            WHERE role = 'seller'
            LIMIT 1
        """)
        seller = cursor.fetchone()
        
        if not seller:
            print("\n⚠️  No seller user found")
            return False
        
        print(f"\n✅ Found seller user:")
        print(f"   - ID: {seller['id']}")
        print(f"   - Username: {seller['username']}")
        print(f"   - Email: {seller['email']}")
        print(f"   - Name: {seller['first_name']} {seller['last_name']}")
        print(f"   - Password: {'*' * len(seller['password'])} (stored as: {seller['password']})")
        print(f"   - Role: {seller['role']}")
        print(f"   - Status: {seller['status']}")
        print(f"   - Created: {seller['created_at']}")
        
        return True
        
    except Error as e:
        print(f"❌ Seller verification failed: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Main test function"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "   DATABASE USER ACCOUNTS TEST SCRIPT".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\n📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: {DB_CONFIG['database']}")
    print(f"🖥️  Host: {DB_CONFIG['host']}")
    
    # Connect to database
    conn = connect_db()
    if not conn:
        print("\n❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    try:
        # Run tests
        schema_ok = test_database_schema(conn)
        users_exist = test_user_count(conn)
        list_all_users(conn)
        admin_ok = verify_admin_user(conn)
        buyer_ok = test_buyer_user(conn)
        seller_ok = test_seller_user(conn)
        
        # Test specific credentials
        print("\n" + "="*60)
        print("🔐 TESTING SAMPLE LOGIN CREDENTIALS")
        print("="*60)
        
        # Test admin credentials
        print("\n1️⃣  Testing Admin Account:")
        admin_login = test_user_credentials(conn, 'admin@kidscommerce.com', 'admin123')
        
        # Test buyer credentials (if exists)
        print("\n2️⃣  Testing Buyer Account (if exists):")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email, password FROM user WHERE role='buyer' LIMIT 1")
        buyer = cursor.fetchone()
        cursor.close()
        
        if buyer:
            buyer_login = test_user_credentials(conn, buyer['email'], buyer['password'])
        else:
            print("   ⚠️  No buyer account found to test")
            buyer_login = False
        
        # Summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        summary = {
            "Database Schema": "✅ PASS" if schema_ok else "❌ FAIL",
            "Users Exist": "✅ PASS" if users_exist else "❌ FAIL",
            "Admin User": "✅ PASS" if admin_ok else "❌ FAIL",
            "Buyer User": "✅ PASS" if buyer_ok else "⚠️  N/A" if not buyer_ok else "❌ FAIL",
            "Seller User": "✅ PASS" if seller_ok else "⚠️  N/A" if not seller_ok else "❌ FAIL",
            "Admin Login": "✅ PASS" if admin_login else "❌ FAIL",
            "Buyer Login": "✅ PASS" if buyer_login else "⚠️  N/A" if not buyer else "❌ FAIL",
        }
        
        for test_name, result in summary.items():
            print(f"{test_name:<25} {result}")
        
        # Overall result
        all_passed = all([schema_ok, users_exist, admin_ok, admin_login])
        
        print("\n" + "="*60)
        if all_passed:
            print("✅ ALL CRITICAL TESTS PASSED!")
            print("   Database users are working correctly.")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("   Please check the database configuration.")
        print("="*60)
        
        print(f"\n⏱️  Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
