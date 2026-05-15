#!/usr/bin/env python3
"""
Check and fix user ID 25 data in database
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

with app.app_context():
    # Find user 25
    user = db.session.get(User, 25)
    
    if not user:
        print("[ERROR] User ID 25 not found in database")
        sys.exit(1)
    
    print(f"User ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Phone: {user.phone}")
    print(f"Address: {user.address}")
    print(f"Role: {user.role}")
    print(f"Status: {user.status}")
    
    # Check if data is missing
    if not user.first_name or not user.last_name or not user.phone:
        print("\n[WARN] User has missing data!")
        print("Attempting to fix with default values...")
        
        if not user.first_name:
            user.first_name = "Juan"
        if not user.last_name:
            user.last_name = "Buyer"
        if not user.phone:
            user.phone = "09123456789"
        if not user.address:
            user.address = "Sample Address"
        
        db.session.commit()
        print("[OK] User data updated!")
        
        print(f"\nUpdated values:")
        print(f"First Name: {user.first_name}")
        print(f"Last Name: {user.last_name}")
        print(f"Phone: {user.phone}")
        print(f"Address: {user.address}")
    else:
        print("\n[OK] User data looks complete")
