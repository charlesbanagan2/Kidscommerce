import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, User

with app.app_context():
    # Find the user
    user = User.query.filter_by(email='juanrider@gmail.com', role='rider').first()
    
    if user:
        print(f"Found user: {user.first_name} {user.last_name}")
        print(f"Current status: {user.status}")
        print(f"Role: {user.role}")
        
        # Update status to active
        user.status = 'active'
        db.session.commit()
        
        print(f"\n✓ Updated status to: {user.status}")
        print(f"✓ User can now log in!")
    else:
        print("User not found with email juanrider@gmail.com and role rider")
        
    # Show all riders
    print("\n" + "="*60)
    print("All riders in database:")
    print("="*60)
    riders = User.query.filter_by(role='rider').all()
    for r in riders:
        status_icon = "✓" if r.status == 'active' else "⏳" if r.status == 'pending' else "✗"
        print(f"{status_icon} ID {r.id}: {r.first_name} {r.last_name} ({r.email}) - {r.status}")
