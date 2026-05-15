#!/usr/bin/env python3
"""
Diagnostic script to test Supabase database connection
"""
import os
import sys
from dotenv import load_dotenv
from urllib.parse import quote
import socket

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Get configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '')
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', '')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '6543')

print("=" * 60)
print("SUPABASE CONNECTION DIAGNOSTIC")
print("=" * 60)

# 1. Check DNS resolution
print("\n[1] DNS Resolution Check:")
try:
    ip = socket.gethostbyname(SUPABASE_DB_HOST)
    print(f"    ✓ {SUPABASE_DB_HOST} resolves to {ip}")
except socket.gaierror as e:
    print(f"    ✗ FAILED: Cannot resolve {SUPABASE_DB_HOST}")
    print(f"    Error: {e}")
    print("\n    → This is your issue! Supabase host cannot be reached.")
    print("    → Solutions:")
    print("      - Check your internet connection")
    print("      - Verify Supabase project still exists at https://supabase.com")
    print("      - Check if Supabase has regional outages")
    sys.exit(1)

# 2. Check TCP connection
print("\n[2] TCP Connection Check:")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((SUPABASE_DB_HOST, int(SUPABASE_DB_PORT)))
    sock.close()
    if result == 0:
        print(f"    ✓ Port {SUPABASE_DB_PORT} is open")
    else:
        print(f"    ✗ FAILED: Cannot connect to {SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}")
        print(f"    Error code: {result}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    sys.exit(1)

# 3. Check SQLAlchemy connection
print("\n[3] SQLAlchemy Connection Check:")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(SUPABASE_DB_URL, connect_args={'connect_timeout': 5})
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"    ✓ SQLAlchemy connection successful!")
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    print("\n    Likely causes:")
    print("    - Invalid database credentials")
    print("    - Database user doesn't exist")
    print("    - Database is not running")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL CHECKS PASSED - Supabase connection is working!")
print("=" * 60)
