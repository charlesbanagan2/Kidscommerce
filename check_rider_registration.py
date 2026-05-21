"""
Check for rider registration with email cbanagan22@gmail.com
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, User, RiderApplication
from datetime import datetime

with app.app_context():
    print("=" * 80)
    print("CHECKING RIDER REGISTRATION: cbanagan22@gmail.com")
    print("=" * 80)
    
    # Check if user exists
    user = User.query.filter_by(email='cbanagan22@gmail.com').first()
    
    if user:
        print(f"\n✓ USER FOUND:")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Status: {user.status}")
        print(f"  Created At: {user.created_at}")
        print(f"  Phone: {user.phone}")
        
        # Check for rider application
        rider_apps = RiderApplication.query.filter_by(user_id=user.id).all()
        
        if rider_apps:
            print(f"\n✓ RIDER APPLICATION(S) FOUND: {len(rider_apps)}")
            for i, app in enumerate(rider_apps, 1):
                print(f"\n  Application #{i}:")
                print(f"    ID: {app.id}")
                print(f"    Status: {app.status}")
                print(f"    Vehicle Type: {app.vehicle_type}")
                print(f"    Vehicle Number: {app.vehicle_number}")
                print(f"    Applied At: {app.applied_at}")
        else:
            print(f"\n✗ NO RIDER APPLICATION FOUND for user_id={user.id}")
            
    else:
        print(f"\n✗ USER NOT FOUND with email: cbanagan22@gmail.com")
    
    # Check all pending rider applications
    print("\n" + "=" * 80)
    print("ALL PENDING RIDER APPLICATIONS:")
    print("=" * 80)
    
    pending_apps = RiderApplication.query.filter_by(status='pending').order_by(RiderApplication.applied_at.desc()).all()
    
    if pending_apps:
        print(f"\nFound {len(pending_apps)} pending rider application(s):\n")
        for app in pending_apps:
            print(f"  • ID: {app.id} | User: {app.user.first_name} {app.user.last_name} ({app.user.email})")
            print(f"    Status: {app.status} | Applied: {app.applied_at}")
            print(f"    Vehicle: {app.vehicle_type} | Plate: {app.vehicle_number}")
            print()
    else:
        print("\nNo pending rider applications found.")
    
    # Check all pending users with role='rider'
    print("\n" + "=" * 80)
    print("ALL PENDING USERS WITH ROLE='rider':")
    print("=" * 80)
    
    pending_riders = User.query.filter_by(status='pending', role='rider').order_by(User.created_at.desc()).all()
    
    if pending_riders:
        print(f"\nFound {len(pending_riders)} pending rider user(s):\n")
        for user in pending_riders:
            print(f"  • ID: {user.id} | Name: {user.first_name} {user.last_name}")
            print(f"    Email: {user.email}")
            print(f"    Status: {user.status} | Created: {user.created_at}")
            
            # Check if they have rider application
            rider_app = RiderApplication.query.filter_by(user_id=user.id).first()
            if rider_app:
                print(f"    ✓ Has Rider Application (ID: {rider_app.id}, Status: {rider_app.status})")
            else:
                print(f"    ✗ NO Rider Application found")
            print()
    else:
        print("\nNo pending users with role='rider' found.")
    
    print("=" * 80)
