"""
Fix buyer role in database - sets buyer accounts to role='buyer'
Run this once to fix the database issue
"""
import sys
sys.path.insert(0, '/home/user/kids/backend')  # Adjust path as needed

from app import app, db, User

with app.app_context():
    # Find all users with wrong roles
    print("\n=== CHECKING USER ROLES ===\n")
    
    users = User.query.all()
    for user in users:
        print(f"User: {user.first_name} {user.last_name} | Email: {user.email} | Role: {user.role} | Status: {user.status}")
    
    print("\n=== FIXING BUYER ACCOUNTS ===\n")
    
    # Fix: Set buyer accounts to role='buyer'
    # Get users who should be buyers (status='active', role NOT in admin/seller/rider)
    buyers_to_fix = User.query.filter(
        User.role != 'admin',
        User.role != 'seller',
        User.role != 'rider',
        User.status == 'active'
    ).all()
    
    for buyer in buyers_to_fix:
        old_role = buyer.role
        buyer.role = 'buyer'
        print(f"✅ Fixed: {buyer.first_name} {buyer.last_name} ({buyer.email})")
        print(f"   {old_role} → buyer")
    
    # Also explicitly check if any account named 'buyer' or test account needs fixing
    test_buyer = User.query.filter_by(email='buyer@test.com').first()
    if test_buyer and test_buyer.role != 'buyer':
        test_buyer.role = 'buyer'
        print(f"✅ Fixed test buyer: {test_buyer.email} → buyer")
    
    db.session.commit()
    
    print("\n=== VERIFICATION ===\n")
    users = User.query.all()
    for user in users:
        print(f"✓ {user.first_name} {user.last_name} | {user.email} | Role: {user.role}")
    
    print("\n✅ Database fixed! Buyers now have role='buyer'")
