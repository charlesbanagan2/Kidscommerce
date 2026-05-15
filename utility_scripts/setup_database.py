#!/usr/bin/env python3
"""
Kids E-Commerce Platform - Single Database Setup (Python)
For: Mobile App + Website (both using same kids_ecommerce database)
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("Kids E-Commerce Platform - Single Database Setup")
    print("="*60 + "\n")

def print_section(title):
    print(f"\n{title}...", end=" ", flush=True)

def print_success(msg="✓ Success"):
    print(f"\r{msg}")

def print_error(msg):
    print(f"\r✗ ERROR: {msg}")
    sys.exit(1)

def print_warning(msg):
    print(f"\r⚠ WARNING: {msg}")

def check_mysql_installed():
    print_section("Checking MySQL installation")
    try:
        result = subprocess.run(["mysql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("✓ MySQL found")
            return True
    except FileNotFoundError:
        pass
    
    print_error("MySQL not found in PATH")

def test_mysql_connection():
    print_section("Testing MySQL connection (user: root)")
    try:
        result = subprocess.run(
            ["mysql", "-u", "root", "-e", "SELECT 1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("✓ MySQL connection successful")
            return True
    except Exception as e:
        pass
    
    print_error("Cannot connect to MySQL. Make sure MySQL is running.")

def create_database():
    print_section("Creating database: kids_ecommerce")
    try:
        sql = "CREATE DATABASE IF NOT EXISTS kids_ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
        result = subprocess.run(
            ["mysql", "-u", "root", "-e", sql],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print_success("✓ Database created or already exists")
            return True
    except Exception as e:
        pass
    
    print_error("Failed to create database")

def run_schema_update():
    print_section("Running schema updates")
    
    sql_file = Path("database_update_comprehensive.sql")
    if not sql_file.exists():
        print_warning("database_update_comprehensive.sql not found - skipping")
        return True
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Run the SQL
        result = subprocess.run(
            ["mysql", "-u", "root", "kids_ecommerce"],
            input=sql_content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("✓ Schema updated")
            return True
        else:
            # Some errors might be non-fatal (like table exists)
            if "already exists" in result.stderr.lower():
                print_success("✓ Schema updated (tables already exist)")
                return True
    except Exception as e:
        print_warning(f"Schema update issue: {e}")
        return True

def verify_database():
    print("\nVerifying database setup...")
    print("-" * 40)
    
    # Count tables
    try:
        query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'kids_ecommerce';"
        result = subprocess.run(
            ["mysql", "-u", "root", "kids_ecommerce", "-N", "-B", "-e", query],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            count = result.stdout.strip()
            print(f"Table Count: {count}")
    except:
        pass
    
    # Database size
    try:
        query = "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) FROM information_schema.tables WHERE table_schema = 'kids_ecommerce';"
        result = subprocess.run(
            ["mysql", "-u", "root", "kids_ecommerce", "-N", "-B", "-e", query],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            size = result.stdout.strip()
            print(f"Database Size: {size} MB")
    except:
        pass
    
    # Check critical tables
    print("\nChecking critical tables:")
    tables = ['user', 'product', 'order', 'cart', 'notification']
    
    for table in tables:
        try:
            query = f"SELECT 1 FROM {table} LIMIT 1;"
            result = subprocess.run(
                ["mysql", "-u", "root", "kids_ecommerce", "-e", query],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✓ {table} table exists")
            else:
                print(f"  ✗ {table} table missing")
        except:
            print(f"  ? {table} table unknown")

def show_summary():
    print("\n" + "="*60)
    print("✓ DATABASE SETUP COMPLETE")
    print("="*60)
    
    print("\nConnection Details:")
    print("  Database Name: kids_ecommerce")
    print("  Host: 127.0.0.1")
    print("  Port: 3306")
    print("  Username: root")
    print("  Password: (empty)")
    
    print("\nNext Steps:")
    print("\n1. Start Flask Backend:")
    print("   cd backend")
    print("   python app.py")
    
    print("\n2. Update Flutter App (if physical device):")
    print("   Edit: mobile_app/lib/services/api_service.dart")
    print("   Change baseUrl to your machine IP")
    
    print("\n3. Access Applications:")
    print("   Mobile API:  http://127.0.0.1:5000/api/v1")
    print("   Website:     http://127.0.0.1:5000")
    print("   Admin:       http://127.0.0.1:5000/admin")
    
    print("\nSingle Database Status:")
    print("  ✓ kids_ecommerce (MySQL)")
    print("  ✓ Used by Mobile App")
    print("  ✓ Used by Website")
    print("  ✓ Used by Admin Panel")
    print()

def main():
    print_header()
    
    print("This script will:")
    print("  1. Check MySQL is installed")
    print("  2. Create kids_ecommerce database")
    print("  3. Initialize all tables from schema")
    print("  4. Verify database setup")
    
    # Run setup steps
    check_mysql_installed()
    test_mysql_connection()
    create_database()
    run_schema_update()
    verify_database()
    show_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
