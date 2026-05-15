#!/usr/bin/env python3
"""
Supabase Credential Validator
Helps verify your Supabase project is still accessible
"""
import os
import sys
from dotenv import load_dotenv
import json

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

print("=" * 80)
print("SUPABASE CREDENTIAL VERIFICATION")
print("=" * 80)
print()

# Extract credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '').strip()
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '').strip()
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', '').strip()
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', '').strip()
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '').strip()
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', '').strip()
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '6543').strip()

print("[1] Current Configuration (from backend/.env)")
print("-" * 80)
print(f"SUPABASE_URL:           {SUPABASE_URL}")
print(f"SUPABASE_DB_HOST:       {SUPABASE_DB_HOST}")
print(f"SUPABASE_DB_USER:       {SUPABASE_DB_USER}")
print(f"SUPABASE_DB_NAME:       {SUPABASE_DB_NAME}")
print(f"SUPABASE_DB_PORT:       {SUPABASE_DB_PORT}")
print(f"SUPABASE_KEY:           {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY:           NOT SET")
print(f"SUPABASE_SERVICE_KEY:   {SUPABASE_SERVICE_KEY[:20]}..." if SUPABASE_SERVICE_KEY else "SUPABASE_SERVICE_KEY:   NOT SET")
print()

# Validation checks
errors = []
warnings = []

print("[2] Configuration Validation")
print("-" * 80)

if not SUPABASE_URL:
    errors.append("❌ SUPABASE_URL is not set")
else:
    if not SUPABASE_URL.startswith('https://'):
        errors.append(f"❌ SUPABASE_URL should start with https://: {SUPABASE_URL}")
    else:
        print("✓ SUPABASE_URL format is correct")

if not SUPABASE_DB_HOST:
    errors.append("❌ SUPABASE_DB_HOST is not set")
else:
    if 'supabase.co' in SUPABASE_DB_HOST:
        print("✓ SUPABASE_DB_HOST looks valid")
    else:
        warnings.append(f"⚠ SUPABASE_DB_HOST doesn't contain 'supabase.co': {SUPABASE_DB_HOST}")

if not SUPABASE_DB_USER:
    warnings.append("⚠ SUPABASE_DB_USER not set (may use default 'postgres')")
else:
    print("✓ SUPABASE_DB_USER is set")

if not SUPABASE_DB_PASSWORD:
    errors.append("❌ SUPABASE_DB_PASSWORD is not set")
else:
    print("✓ SUPABASE_DB_PASSWORD is set")

if not SUPABASE_KEY:
    warnings.append("⚠ SUPABASE_KEY (public key) not set")
else:
    print("✓ SUPABASE_KEY is set")

if not SUPABASE_SERVICE_KEY:
    warnings.append("⚠ SUPABASE_SERVICE_KEY (secret key) not set")
else:
    print("✓ SUPABASE_SERVICE_KEY is set")

# Print warnings and errors
print()
if warnings:
    print("[3] Warnings")
    print("-" * 80)
    for warning in warnings:
        print(warning)
    print()

if errors:
    print("[4] ERRORS - Must Fix")
    print("-" * 80)
    for error in errors:
        print(error)
    print()
    print("RECOVERY:")
    print("1. Go to: https://supabase.com")
    print("2. Log in and select your project")
    print("3. Go to: Settings → Database → Connection String")
    print("4. Copy the connection details")
    print("5. Update backend/.env with the correct values")
    print()
    sys.exit(1)
else:
    print("[3] All required credentials are set!")
    print("-" * 80)
    print()
    print("Next steps:")
    print("1. Run: python fix_supabase.py")
    print("   (This will test the actual connection)")
    print()
    print("If you still get connection errors:")
    print("- Check: https://status.supabase.com")
    print("- Verify your Supabase project is not paused")
    print("- Try creating a new Supabase project")

print()
print("=" * 80)
