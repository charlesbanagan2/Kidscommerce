#!/usr/bin/env python3
"""
Google Login Integration Test
Tests the complete flow: Mobile App -> Backend API -> Database (Supabase)
"""

import json
import sys
import os
import requests
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

# Test Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_KEY')

print_header("🔐 GOOGLE LOGIN INTEGRATION TEST")

# Step 1: Check environment
print_info("Step 1: Checking environment configuration...")
if not SUPABASE_URL:
    print_error("SUPABASE_URL not configured")
    sys.exit(1)
if not SUPABASE_API_KEY:
    print_error("SUPABASE_KEY not configured")
    sys.exit(1)
print_success("Supabase credentials loaded")
print_info(f"Backend URL: {BACKEND_URL}")
print_info(f"Supabase Project: {SUPABASE_URL.split('.')[0].split('://')[-1]}")

# Step 2: Test backend connectivity
print_header("Step 2: Testing Backend Connectivity")
try:
    response = requests.get(f"{BACKEND_URL}/", timeout=5)
    if response.status_code in [200, 301, 302, 404]:
        print_success(f"Backend is reachable (Status: {response.status_code})")
    else:
        print_error(f"Backend returned unexpected status: {response.status_code}")
except Exception as e:
    print_error(f"Cannot reach backend: {str(e)}")
    print_warning("Make sure backend is running on http://localhost:5000")

# Step 3: Check if Google login endpoint exists
print_header("Step 3: Checking Google Login Endpoint")
try:
    # Try with a test request (will fail but we're just checking endpoint exists)
    response = requests.post(
        f"{BACKEND_URL}/api/v1/google-login",
        json={'id_token': 'test', 'access_token': 'test'},
        timeout=5
    )
    
    # We expect an error, but the endpoint should exist and respond
    if response.status_code == 401:
        print_success("✨ Endpoint exists and validates tokens correctly")
        error_data = response.json()
        print_info(f"Response: {error_data.get('error', 'Invalid token')}")
    elif response.status_code == 500:
        print_warning("Endpoint exists but returned 500 error")
        try:
            error_data = response.json()
            print_info(f"Error details: {error_data.get('error', 'Unknown')}")
        except:
            pass
    else:
        print_warning(f"Endpoint returned status: {response.status_code}")
        print_info(f"Response: {response.text[:200]}")
except requests.exceptions.ConnectionError:
    print_error("Cannot connect to backend - ensure it's running")
except Exception as e:
    print_error(f"Error testing endpoint: {str(e)}")

# Step 4: Check Supabase connectivity
print_header("Step 4: Testing Supabase Connectivity")
try:
    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}'
    }
    
    # Try to list users table
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/user?limit=1",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print_success("✨ Supabase database is accessible")
        try:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print_info(f"User table contains {count} sample records")
        except:
            pass
    elif response.status_code == 401:
        print_error("Supabase API key is invalid or expired")
    elif response.status_code == 404:
        print_error("Supabase project not found or endpoint incorrect")
    else:
        print_warning(f"Supabase returned status {response.status_code}")
        
except Exception as e:
    print_error(f"Cannot connect to Supabase: {str(e)}")
    print_warning("Check SUPABASE_URL and SUPABASE_KEY environment variables")

# Step 5: Check for OAuth table in database
print_header("Step 5: Checking Database Schema")
try:
    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}'
    }
    
    # Check if oauth table exists
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/oauth?limit=1",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print_success("OAuth table exists in database")
    elif response.status_code == 404:
        print_error("⚠️  OAuth table NOT found in database")
        print_warning("Google login requires an 'oauth' table to store provider mappings")
        print_info("Missing columns might be:")
        print_info("  - id (Primary Key)")
        print_info("  - user_id (Foreign Key to user)")
        print_info("  - provider (e.g., 'google')")
        print_info("  - provider_user_id (Google sub claim)")
        print_info("  - token (JSON)")
        print_info("  - created_at")
    else:
        print_warning(f"Cannot determine OAuth table status: {response.status_code}")
        
except Exception as e:
    print_error(f"Cannot check OAuth table: {str(e)}")

# Step 6: Generate Test Report
print_header("📊 DIAGNOSTIC SUMMARY")

print(f"""
{Colors.BOLD}Configuration Status:{Colors.ENDC}
  • Backend URL: {BACKEND_URL}
  • Supabase Project: {SUPABASE_URL}
  • Database API: {SUPABASE_URL}/rest/v1
  
{Colors.BOLD}Google Login Flow:{Colors.ENDC}
  1. Mobile App (Flutter): Authenticates with Google
  2. Gets: id_token, access_token
  3. Sends to: POST /api/v1/google-login
  4. Backend: Validates with Google, looks up/creates user
  5. Database: Saves user and OAuth record
  6. Returns: JWT tokens and user data to mobile app

{Colors.BOLD}Database Requirements:{Colors.ENDC}
  • user table: Must have email, first_name, last_name, role, status
  • oauth table: Must link users to Google accounts
  • Both should have proper indexes and constraints

{Colors.BOLD}Common Issues:{Colors.ENDC}
  ❌ Missing oauth table: Google login will fail to create accounts
  ❌ Invalid API key: Cannot save to database
  ❌ Backend offline: Mobile app cannot communicate
  ❌ No token validation: Security risk, invalid tokens accepted
  ❌ Pending user creation: Users must be approved before login
""")

print_header("✅ NEXT STEPS")
print(f"""
1. Start the backend server:
   cd backend
   python app.py

2. Ensure Supabase tables exist (oauth table especially)

3. Test with mock Google token:
   curl -X POST http://localhost:5000/api/v1/google-login \\
     -H "Content-Type: application/json" \\
     -d '{{"id_token": "test_token", "access_token": "test"}}'

4. Check mobile app logs for API responses:
   - Use DevTools in Flutter
   - Look for /api/v1/google-login requests
   - Verify token storage in SharedPreferences

5. Monitor database for new users:
   - Check user table for new records
   - Verify oauth records created
   - Ensure status is 'active' (not 'pending')
""")
