"""
Test script to verify SECRET_KEY and JWT_SECRET_KEY are properly loaded from .env
This script checks that the keys are loaded without fallback defaults
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def test_secret_keys():
    """Test that secret keys are properly configured"""
    print("\n" + "="*60)
    print("SECRET KEYS CONFIGURATION TEST")
    print("="*60)
    
    # Test SECRET_KEY
    print("\n1. Testing SECRET_KEY (Flask Sessions):")
    print("-" * 60)
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print(f"✅ SECRET_KEY is set")
        print(f"   Length: {len(secret_key)} characters")
        print(f"   Preview: {secret_key[:20]}...{secret_key[-10:]}")
        
        # Check strength
        if len(secret_key) >= 32:
            print("   ✅ Length is sufficient (>= 32 chars)")
        else:
            print(f"   ⚠️  Length is weak (< 32 chars)")
    else:
        print("❌ SECRET_KEY is NOT set!")
        print("   Add SECRET_KEY to your .env file")
        print("   Example: SECRET_KEY=\"your-secret-key-here\"")
    
    # Test JWT_SECRET_KEY
    print("\n2. Testing JWT_SECRET_KEY (Mobile API):")
    print("-" * 60)
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if jwt_secret:
        print(f"✅ JWT_SECRET_KEY is set")
        print(f"   Length: {len(jwt_secret)} characters")
        print(f"   Preview: {jwt_secret[:20]}...{jwt_secret[-10:]}")
        
        # Check strength
        if len(jwt_secret) >= 32:
            print("   ✅ Length is sufficient (>= 32 chars)")
        else:
            print(f"   ⚠️  Length is weak (< 32 chars)")
    else:
        print("❌ JWT_SECRET_KEY is NOT set!")
        print("   Add JWT_SECRET_KEY to your .env file")
        print("   Example: JWT_SECRET_KEY=\"your-jwt-secret-here\"")
    
    # Test other important keys
    print("\n3. Testing Other Configuration:")
    print("-" * 60)
    
    # Email configuration
    mail_sender = os.getenv('MAIL_SENDER')
    mail_password = os.getenv('MAIL_APP_PASSWORD')
    print(f"   MAIL_SENDER: {'✅ Set' if mail_sender else '❌ Not set'}")
    print(f"   MAIL_APP_PASSWORD: {'✅ Set' if mail_password else '❌ Not set'}")
    
    # Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")
    
    # Email verification
    email_verify_key = os.getenv('EMAILLISTVERIFY_API_KEY')
    print(f"   EMAILLISTVERIFY_API_KEY: {'✅ Set' if email_verify_key else '❌ Not set'}")
    
    # Google OAuth
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    print(f"   GOOGLE_CLIENT_ID: {'✅ Set' if google_client_id else '❌ Not set'}")
    print(f"   GOOGLE_CLIENT_SECRET: {'✅ Set' if google_client_secret else '❌ Not set'}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_critical_set = secret_key and jwt_secret
    
    if all_critical_set:
        print("✅ All CRITICAL keys are configured!")
        print("   Your application is ready to start.")
        print("\n   To start the server:")
        print("   python backend/app.py")
    else:
        print("❌ Some CRITICAL keys are missing!")
        print("   Your application will NOT start.")
        print("\n   Required keys:")
        if not secret_key:
            print("   - SECRET_KEY")
        if not jwt_secret:
            print("   - JWT_SECRET_KEY")
        print("\n   Add these to your .env file and try again.")
    
    print("="*60 + "\n")
    
    return all_critical_set

def generate_strong_keys():
    """Generate strong random keys for SECRET_KEY and JWT_SECRET_KEY"""
    import secrets
    
    print("\n" + "="*60)
    print("GENERATE STRONG KEYS")
    print("="*60)
    print("\nUse these commands to generate strong random keys:\n")
    
    print("Python:")
    print("  import secrets")
    print("  print(secrets.token_urlsafe(32))")
    
    print("\nOr use these pre-generated keys:")
    print("-" * 60)
    
    secret_key = secrets.token_urlsafe(32)
    jwt_secret = secrets.token_urlsafe(32)
    
    print(f"\nSECRET_KEY=\"{secret_key}\"")
    print(f"JWT_SECRET_KEY=\"{jwt_secret}\"")
    
    print("\nCopy these to your .env file!")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Test current configuration
    all_set = test_secret_keys()
    
    # Offer to generate new keys
    if not all_set:
        print("\n💡 TIP: Need to generate strong keys?")
        response = input("   Generate new keys? (y/n): ").strip().lower()
        if response == 'y':
            generate_strong_keys()
