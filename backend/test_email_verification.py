"""
Test script for EmailListVerify API integration
Tests the email verification functionality before using in production
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
API_KEY = os.getenv('EMAILLISTVERIFY_API_KEY') or os.getenv('EMAILLISTVERIFY_SECRET')
API_URL = "https://apps.emaillistverify.com/api/verifyEmail"

def verify_email_with_emaillistverify(address: str):
    """
    Validate an email using the EmailListVerify HTTP API.
    This mimics the function in app.py
    """
    address = (address or "").strip()
    if not address or '@' not in address:
        return False

    if not API_KEY:
        print("⚠️  No API key - would skip validation")
        return True

    try:
        resp = requests.get(
            API_URL,
            params={"secret": API_KEY, "email": address},
            timeout=8,
        )
        if resp.status_code != 200:
            print(f"⚠️  API returned HTTP {resp.status_code}")
            return False
            
        status = (resp.text or "").strip().lower()
        domain = address.split('@', 1)[-1].lower()
        
        # 'ok' means deliverable
        if status == 'ok':
            return True
        
        # Block clearly invalid statuses
        invalid_statuses = {
            'fail', 'failed', 'invalid', 'error', 'bad', 
            'unknown_email', 'unknown_user', 'no_mailbox', 'does_not_exist',
            'invalid_mx',  # Invalid MX records
            'disposable',  # Disposable/temporary email
            'spamtrap'     # Known spam trap
        }
        if status in invalid_statuses:
            return False
        
        # Be strict for gmail.com
        if domain == 'gmail.com' and status != 'ok':
            return False
        
        # For other responses, fail open
        return True
        
    except Exception as e:
        print(f"⚠️  API error: {e}")
        return False

def test_email_verification(email):
    """Test email verification with EmailListVerify API"""
    print(f"\n{'='*60}")
    print(f"Testing email: {email}")
    print(f"{'='*60}")
    
    if not API_KEY:
        print("❌ ERROR: API key not found in .env file")
        print("   Please add EMAILLISTVERIFY_API_KEY to your .env file")
        return
    
    print(f"✅ API Key found: {API_KEY[:10]}...{API_KEY[-10:]}")
    print(f"📡 Calling API: {API_URL}")
    
    try:
        # Call EmailListVerify API
        response = requests.get(
            API_URL,
            params={"secret": API_KEY, "email": email},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            status = response.text.strip().lower()
            
            # Now test with our validation function
            is_valid = verify_email_with_emaillistverify(email)
            
            if is_valid:
                print(f"\n✅ VALID EMAIL: {email}")
                print(f"   Status: {status}")
                print("   Registration would be ALLOWED")
            else:
                print(f"\n❌ INVALID EMAIL: {email}")
                print(f"   Status: {status}")
                print("   Registration would be BLOCKED")
        else:
            print(f"\n❌ API ERROR: HTTP {response.status_code}")
            print("   Registration would be BLOCKED")
            
    except requests.exceptions.Timeout:
        print("\n⏱️  TIMEOUT: API took too long to respond")
        print("   Registration would be BLOCKED")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("   Registration would be BLOCKED")

def main():
    """Run email verification tests"""
    print("\n" + "="*60)
    print("EMAIL VERIFICATION TEST SCRIPT")
    print("EmailListVerify API Integration")
    print("="*60)
    
    # Test cases
    test_emails = [
        "gbanagan33@gmail.com",  # Your real email (should be valid)
        "test@gmail.com",  # Common test email (spamtrap - should be blocked)
        "nonexistent123456789@gmail.com",  # Non-existent Gmail (may pass if API says 'ok')
        "invalid@fakeemail.com",  # Fake domain (invalid_mx - should be blocked)
        "test@tempmail.com",  # Disposable email (should be blocked)
    ]
    
    for email in test_emails:
        test_email_verification(email)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n📋 SUMMARY:")
    print("✅ = Email is valid, registration allowed")
    print("❌ = Email is invalid, registration blocked")
    print("\n🔍 Status Meanings:")
    print("  • ok = Valid, deliverable email")
    print("  • spamtrap = Known spam trap (BLOCKED)")
    print("  • invalid_mx = Domain can't receive email (BLOCKED)")
    print("  • disposable = Temporary email service (BLOCKED)")
    print("\nTo test in mobile app:")
    print("1. Restart Flask server: python backend/app.py")
    print("2. Open mobile app and try registration")
    print("3. Use test emails above to see validation in action")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
