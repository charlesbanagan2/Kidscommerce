#!/usr/bin/env python3
"""
Test script for Email Verification Integration
Run this to verify your email verification setup is working
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_email_verification():
    """Test the email verification endpoints"""
    
    print("=" * 70)
    print("EMAIL VERIFICATION API TEST")
    print("=" * 70)
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against: {BASE_URL}\n")
    
    # Test 1: Check if email verification is enabled
    print("[1] Checking Email Verification Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/verify-email-status")
        if response.status_code == 200:
            status = response.json()
            print(f"    ✓ Status: {json.dumps(status, indent=6)}")
        else:
            print(f"    ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"    ✗ Connection error: {e}")
        print(f"    → Make sure Flask app is running on {BASE_URL}")
        return
    
    # Test 2: Verify a single email
    print("\n[2] Testing Single Email Verification...")
    test_emails = [
        "test@example.com",
        "invalid.email",
        "user@gmail.com"
    ]
    
    for email in test_emails:
        try:
            payload = {"email": email}
            response = requests.post(
                f"{BASE_URL}/api/verify-email",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                valid = "✓" if result.get('valid') else "✗"
                api = "API" if result.get('api_used') else "Local"
                print(f"    {valid} {email:30} → {result.get('reason'):30} ({api})")
            else:
                print(f"    ✗ {email:30} → Error: {response.status_code}")
        except Exception as e:
            print(f"    ✗ {email:30} → {str(e)[:50]}")
    
    # Test 3: Batch verify emails
    print("\n[3] Testing Batch Email Verification...")
    batch_emails = [
        "john@gmail.com",
        "jane@yahoo.com",
        "invalid-email",
        "test123@example.com"
    ]
    
    try:
        payload = {"emails": batch_emails}
        response = requests.post(
            f"{BASE_URL}/api/verify-emails",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            results = response.json()
            print(f"    ✓ Verified {len(results)} emails:")
            for email, result in results.items():
                valid = "✓" if result.get('valid') else "✗"
                print(f"        {valid} {email:30} → {result.get('reason')}")
        else:
            print(f"    ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_email_verification()
