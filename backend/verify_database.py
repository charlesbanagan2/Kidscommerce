"""
Script to verify database connection and list all users
"""
from app import app, db, User
import os

print("=" * 80)
print("DATABASE CONNECTION VERIFICATION")
print("=" * 80)

print("\nFlask App Database Configuration:")
print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
print(f"Supabase URL: {app.config.get('SUPABASE_URL', 'Not set')}")

with app.app_context():
    # Test database connection
    try:
        db.session.execute(db.text("SELECT 1"))
        print("Database Connection: SUCCESS")
    except Exception as e:
        print(f"Database Connection: FAILED - {e}")
    
    # Count total users
    total_users = User.query.count()
    print(f"\nTotal users in database: {total_users}")
    
    # List all users
    print("\n" + "=" * 80)
    print("ALL USERS IN DATABASE")
    print("=" * 80)
    print(f"{'ID':<5} {'Email':<40} {'Role':<10} {'Status':<10}")
    print("-" * 80)
    
    users = User.query.order_by(User.id.desc()).all()
    for user in users:
        print(f"{user.id:<5} {user.email:<40} {user.role:<10} {user.status:<10}")
    
    print("=" * 80)
    
    # Search for specific email
    print("\nSearching for: charlesgabrielle.banagan@lspu.edu.ph")
    target_user = User.query.filter_by(email='charlesgabrielle.banagan@lspu.edu.ph').first()
    if target_user:
        print("FOUND in database:")
        print(f"  ID: {target_user.id}")
        print(f"  Name: {target_user.first_name} {target_user.last_name}")
        print(f"  Email: {target_user.email}")
        print(f"  Phone: {target_user.phone}")
        print(f"  Address: {target_user.address}")
        print(f"  Role: {target_user.role}")
        print(f"  Status: {target_user.status}")
    else:
        print("NOT FOUND in database")
    
    print("\n" + "=" * 80)
    print("If you see this user in this list, it exists in your configured backend datastore.")
    print("If you do not see expected records, verify Supabase credentials and target project.")
    print("=" * 80)
