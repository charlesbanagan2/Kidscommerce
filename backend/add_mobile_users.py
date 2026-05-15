"""
Script to manually add mobile app users to MySQL database
Use this when mobile app registrations failed due to backend connectivity issues
"""
from app import app, db, User, bcrypt

def add_user(first_name, last_name, email, password, phone, address, role='buyer'):
    """Add a user to the database"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"[ERROR] User with email {email} already exists (ID: {existing_user.id})")
            return None
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            phone=phone,
            address=address,
            role=role,
            status='pending',  # Requires admin approval
            email_verified=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"[SUCCESS] User created successfully:")
        print(f"   ID: {user.id}")
        print(f"   Name: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        print(f"   Status: pending (requires admin approval)")
        print()
        
        return user

def list_all_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.order_by(User.id.desc()).all()
        print(f"\n[LIST] Total users in database: {len(users)}")
        print("-" * 80)
        for user in users:
            print(f"ID: {user.id:3} | {user.email:30} | {user.role:10} | {user.status:10}")
        print("-" * 80)

if __name__ == '__main__':
    print("=" * 80)
    print("MOBILE APP USER RECOVERY SCRIPT")
    print("=" * 80)
    print("\nThis script helps you add users that were lost due to mobile app registration failures.\n")
    
    # List existing users
    list_all_users()
    
    print("\n" + "=" * 80)
    print("ADD NEW USERS")
    print("=" * 80)
    
    # Example usage - uncomment and modify to add users
    # add_user(
    #     first_name='John',
    #     last_name='Doe',
    #     email='john.doe@gmail.com',
    #     password='YourPassword123@',
    #     phone='12345678901',
    #     address='123 Test Street',
    #     role='buyer'
    # )
    
    print("\nTo add users, uncomment the add_user() calls in this script and run it again.")
    print("Make sure to:")
    print("1. Use Gmail addresses (required by system)")
    print("2. Password must be 8-12 characters with uppercase, lowercase, number, and special character")
    print("3. Phone must be exactly 11 digits")
