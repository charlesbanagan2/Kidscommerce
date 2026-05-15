#!/usr/bin/env python3
"""
Supabase Connection Recovery Script
This script will help diagnose and fix your database connection
"""
import os
import sys
import socket
import requests
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', '')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '6543')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '')

print("=" * 80)
print("SUPABASE CONNECTION RECOVERY TOOLKIT")
print("=" * 80)
print()

# STEP 1: Check basic connectivity
print("[STEP 1] Network Connectivity Check")
print("-" * 80)

print("\n1.1 Testing Internet Connection...")
try:
    response = requests.get('https://8.8.8.8', timeout=5)
    print("    ✓ Internet connection: OK")
except:
    print("    ✗ CRITICAL: No internet connection")
    print("    → Connect to WiFi/network before continuing")
    sys.exit(1)

print("\n1.2 Testing DNS Resolution...")
try:
    ip = socket.gethostbyname(SUPABASE_DB_HOST)
    print(f"    ✓ {SUPABASE_DB_HOST}")
    print(f"      resolves to: {ip}")
except socket.gaierror as e:
    print(f"    ✗ FAILED: DNS cannot resolve host")
    print(f"    Error: {e}")
    print()
    print("    SOLUTIONS:")
    print("    1. Clear DNS cache:")
    print("       ipconfig /flushdns")
    print("    2. Try alternate DNS servers in Network Settings:")
    print("       - Google DNS: 8.8.8.8, 8.8.4.4")
    print("       - Cloudflare: 1.1.1.1, 1.0.0.1")
    print("    3. Restart your router")
    print("    4. Check Supabase status: https://status.supabase.com")
    sys.exit(1)

print("\n1.3 Testing TCP Connection to Port 6543...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((SUPABASE_DB_HOST, int(SUPABASE_DB_PORT)))
    sock.close()
    if result == 0:
        print(f"    ✓ Port 6543 is open")
    else:
        print(f"    ✗ FAILED: Cannot connect to port 6543")
        print(f"    Error code: {result}")
        print()
        print("    SOLUTIONS:")
        print("    - Supabase server may be down")
        print("    - Check: https://status.supabase.com")
        print("    - Firewall may be blocking port 6543")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    sys.exit(1)

# STEP 2: Verify Supabase Project
print("\n" + "=" * 80)
print("[STEP 2] Verify Supabase Project Status")
print("-" * 80)

print("\n2.1 Checking Supabase API Health...")
try:
    # Try to reach Supabase REST API
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/",
        timeout=10,
        headers={'apikey': os.getenv('SUPABASE_KEY', '')}
    )
    if response.status_code in [200, 401, 403]:
        print(f"    ✓ Supabase API is responding (status: {response.status_code})")
    else:
        print(f"    ✗ Supabase API returned: {response.status_code}")
except Exception as e:
    print(f"    ✗ Cannot reach Supabase API: {str(e)[:100]}")
    print()
    print("    SOLUTIONS:")
    print("    - Verify SUPABASE_URL is correct: " + SUPABASE_URL)
    print("    - Check Supabase console at: https://supabase.com")
    print("    - Project may be paused/deleted")

# STEP 3: Test Database Credentials
print("\n" + "=" * 80)
print("[STEP 3] Test Database Credentials")
print("-" * 80)

print("\n3.1 Checking Database URL Configuration...")
print(f"    Host: {SUPABASE_DB_HOST}")
print(f"    Port: {SUPABASE_DB_PORT}")
print(f"    User: {os.getenv('SUPABASE_DB_USER', 'postgres')}")
print(f"    Database: {os.getenv('SUPABASE_DB_NAME', 'postgres')}")
print(f"    URL: {SUPABASE_DB_URL[:50]}...")

print("\n3.2 Testing SQLAlchemy Connection...")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(
        SUPABASE_DB_URL,
        connect_args={'connect_timeout': 10},
        echo=False
    )
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as connection_test"))
        print("    ✓ SQLAlchemy connection: SUCCESSFUL!")
        print("    → Your database is working!")
except ImportError:
    print("    ⚠ SQLAlchemy not installed, skipping connection test")
except Exception as e:
    error_msg = str(e)
    print(f"    ✗ FAILED: {error_msg[:200]}")
    print()
    print("    SOLUTIONS:")
    if "password" in error_msg.lower():
        print("    - Password may be incorrect in .env file")
        print("    - Check: SUPABASE_DB_PASSWORD")
    elif "could not translate" in error_msg.lower():
        print("    - DNS resolution failed (see Step 1)")
    elif "timeout" in error_msg.lower():
        print("    - Connection timeout - server may be down")
        print("    - Check: https://status.supabase.com")
    elif "could not connect" in error_msg.lower():
        print("    - Cannot reach database server")
        print("    - Check port 6543 is open")
    else:
        print(f"    - {error_msg}")

# STEP 4: Recovery Options
print("\n" + "=" * 80)
print("[STEP 4] Recovery Options")
print("-" * 80)

print("""
If you're still getting errors, try these solutions:

OPTION 1: Reset Supabase Connection
  1. Log in to https://supabase.com
  2. Select your project
  3. Go to Project Settings → Database
  4. Copy the connection string
  5. Update SUPABASE_DB_URL in backend/.env

OPTION 2: Create a New Supabase Project
  1. Go to https://supabase.com
  2. Create a new project
  3. Wait for it to initialize (5-10 minutes)
  4. Copy the new connection details to backend/.env

OPTION 3: Use SQLite for Development (Temporary)
  Run: python switch_to_sqlite.py
  (This creates a local database for testing)

OPTION 4: Check Supabase Status
  Visit: https://status.supabase.com
  - Check if there are any ongoing incidents
  - Check your project region
""")

print("=" * 80)
print("DONE")
print("=" * 80)
