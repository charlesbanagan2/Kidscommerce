#!/usr/bin/env python3
"""
Query MySQL Database for Test Users
"""

import mysql.connector
from mysql.connector import Error

def connect_to_mysql():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='kids_ecommerce',
            port=3306
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Connected to MySQL Server version {db_info}")
            return connection
        
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return None

def get_all_tables(connection):
    """Get all tables in database"""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\n=== DATABASE TABLES ===")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        return [t[0] for t in tables]
    except Error as e:
        print(f"Error: {e}")
        return []

def get_users(connection):
    """Get all users from database"""
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, email, first_name, last_name, role, status, phone, password 
            FROM user 
            LIMIT 20
        """)
        users = cursor.fetchall()
        
        print("\n=== USERS IN DATABASE ===")
        for user in users:
            print(f"\nID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Role: {user['role']}")
            print(f"  Status: {user['status']}")
            print(f"  Phone: {user['phone']}")
            print(f"  Password Hash: {user['password'][:50]}...")
        
        cursor.close()
        return users
    except Error as e:
        print(f"Error: {e}")
        return []

def get_table_structure(connection, table_name):
    """Get table structure"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print(f"\n=== TABLE STRUCTURE: {table_name} ===")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

def main():
    connection = connect_to_mysql()
    
    if not connection:
        print("\nTrying alternative connection parameters...")
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='kids_ecommerce'
            )
            if connection.is_connected():
                print("✅ Connected with alternative credentials")
        except Error as e:
            print(f"❌ Failed with alternative credentials: {e}")
            return
    
    if connection:
        try:
            tables = get_all_tables(connection)
            
            if 'user' in tables:
                get_users(connection)
                get_table_structure(connection, 'user')
            else:
                print("\n❌ 'user' table not found")
                if tables:
                    print("Available tables:", tables)
        
        finally:
            connection.close()
            print("\n✅ MySQL connection closed")

if __name__ == "__main__":
    main()
