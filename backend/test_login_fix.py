from app import app, get_data

with app.app_context():
    # Test getting user from local database
    users = get_data('user', filters={'email': 'juanrider@gmail.com'})
    
    if users and len(users) > 0:
        user = users[0]
        print("SUCCESS! User found in local database:")
        print(f"  Email: {user.get('email')}")
        print(f"  Password: {user.get('password')}")
        print(f"  Role: {user.get('role')}")
        print(f"  Status: {user.get('status')}")
        print(f"\nLogin should now work with:")
        print(f"  Email: juanrider@gmail.com")
        print(f"  Password: Rider@1234")
    else:
        print("FAILED: User not found")
