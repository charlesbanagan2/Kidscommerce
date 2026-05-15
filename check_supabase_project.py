#!/usr/bin/env python3
"""
Supabase Project Status Checker
Helps verify if your Supabase project still exists and is active
"""
import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '').strip()

print("=" * 80)
print("SUPABASE PROJECT STATUS CHECKER")
print("=" * 80)
print()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY not found in .env")
    print()
    print("Please check your backend/.env file has:")
    print("  SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co")
    print("  SUPABASE_KEY=sb_publishable_...")
    sys.exit(1)

print(f"[1] Checking Project: {SUPABASE_URL}")
print("-" * 80)
print()

# Test 1: Can we reach the Supabase API?
print("1.1 Testing Supabase API Health...")
try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        timeout=10,
        headers={'apikey': SUPABASE_KEY}
    )
    
    if response.status_code == 200:
        print("    ✓ API is healthy and responding")
    elif response.status_code == 401:
        print("    ⚠ API returned 401 Unauthorized")
        print("    → SUPABASE_KEY may be invalid")
    elif response.status_code == 403:
        print("    ⚠ API returned 403 Forbidden")
        print("    → SUPABASE_KEY may be invalid or expired")
    elif response.status_code == 404:
        print("    ❌ API returned 404 Not Found")
        print("    → Project may not exist or URL is incorrect")
    else:
        print(f"    ⚠ API returned status: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("    ❌ API request timed out (10 seconds)")
    print("    → Supabase server is not responding")
except requests.exceptions.ConnectionError as e:
    print(f"    ❌ Cannot connect to Supabase: {str(e)[:100]}")
    print("    → Check your internet connection")
except Exception as e:
    print(f"    ❌ Error: {str(e)[:100]}")

# Test 2: Try to fetch metadata
print()
print("1.2 Attempting to fetch project metadata...")
try:
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        timeout=10,
        headers={
            'apikey': SUPABASE_KEY,
            'Accept': 'application/json'
        }
    )
    
    if response.status_code in [200, 401, 403]:
        print("    ✓ Project exists and is accessible")
    else:
        print(f"    ✗ Project returned error: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        
except Exception as e:
    print(f"    ✗ Error: {str(e)[:100]}")

# Test 3: Try RealTime endpoint
print()
print("1.3 Testing RealTime Connection...")
try:
    response = requests.get(
        f"{SUPABASE_URL}/realtime/v1/",
        timeout=10,
        headers={'apikey': SUPABASE_KEY}
    )
    
    if response.status_code in [200, 401, 403]:
        print("    ✓ RealTime server is available")
    else:
        print(f"    ⚠ RealTime server returned: {response.status_code}")
        
except Exception as e:
    print(f"    ⚠ RealTime connection error: {str(e)[:100]}")

# Test 4: Get project info
print()
print("1.4 Retrieving Project Information...")
try:
    # Try to get any table to verify database is working
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/information_schema.tables?select=table_schema,table_name",
        timeout=10,
        headers={'apikey': SUPABASE_KEY}
    )
    
    if response.status_code == 200:
        try:
            tables = response.json()
            print(f"    ✓ Database is accessible")
            print(f"    ✓ Found {len(tables)} tables/views")
            
            # List tables
            user_tables = [t for t in tables if t['table_schema'] == 'public']
            if user_tables:
                print(f"    ✓ Your tables ({len(user_tables)}):")
                for table in user_tables[:10]:
                    print(f"        - {table['table_name']}")
        except:
            print("    ✓ Database is accessible (couldn't parse tables)")
    else:
        print(f"    ⚠ Database query returned: {response.status_code}")
        
except Exception as e:
    print(f"    ⚠ Could not query database: {str(e)[:100]}")

# Summary
print()
print("=" * 80)
print("SUMMARY")
print("-" * 80)
print()
print("If you see ✓ marks above: Your Supabase project is active and working!")
print()
print("If you see ❌ marks above: There's a problem with your project.")
print("  - Project may be paused/deleted")
print("  - Your credentials may be incorrect")
print("  - Network connectivity issue")
print()
print("Next steps:")
print("1. Verify credentials: python validate_supabase_credentials.py")
print("2. Test connection: python fix_supabase.py")
print("3. If still failing, check https://status.supabase.com")
print()
print("=" * 80)
