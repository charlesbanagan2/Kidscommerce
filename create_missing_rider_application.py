"""
Create missing RiderApplication for existing rider users
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, User, RiderApplication

with app.app_context():
    print("=" * 80)
    print("CREATING MISSING RIDER APPLICATIONS")
    print("=" * 80)
    
    # Find all riders without RiderApplication
    riders_without_app = db.session.query(User).filter(
        User.role == 'rider',
        ~User.id.in_(db.session.query(RiderApplication.user_id))
    ).all()
    
    if not riders_without_app:
        print("\n✓ All riders have RiderApplication records. No action needed.")
    else:
        print(f"\nFound {len(riders_without_app)} rider(s) without RiderApplication:\n")
        
        for user in riders_without_app:
            print(f"  • User ID: {user.id}")
            print(f"    Name: {user.first_name} {user.last_name}")
            print(f"    Email: {user.email}")
            print(f"    Status: {user.status}")
            print(f"    Created: {user.created_at}")
            
            # Create RiderApplication
            try:
                rider_app = RiderApplication(
                    user_id=user.id,
                    vehicle_type='motorcycle',  # Default value
                    vehicle_number='PENDING',   # Placeholder - rider can update later
                    status='pending',
                    applied_at=user.created_at or datetime.utcnow()
                )
                
                db.session.add(rider_app)
                db.session.commit()
                
                print(f"    ✓ RiderApplication created (ID: {rider_app.id})")
                print()
                
            except Exception as e:
                db.session.rollback()
                print(f"    ✗ ERROR: {e}")
                print()
    
    print("=" * 80)
    print("VERIFICATION - All Pending Rider Applications:")
    print("=" * 80)
    
    pending_apps = RiderApplication.query.filter_by(status='pending').order_by(RiderApplication.applied_at.desc()).all()
    
    if pending_apps:
        print(f"\nTotal pending applications: {len(pending_apps)}\n")
        for app in pending_apps:
            print(f"  • ID: {app.id} | User: {app.user.first_name} {app.user.last_name}")
            print(f"    Email: {app.user.email}")
            print(f"    Applied: {app.applied_at}")
            print(f"    Vehicle: {app.vehicle_type} | Plate: {app.vehicle_number}")
            print()
    else:
        print("\nNo pending rider applications.")
    
    print("=" * 80)
    print("✓ DONE!")
    print("=" * 80)
