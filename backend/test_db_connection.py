"""
Test Database Connection Script
Tests the SUPABASE_DB_URL from .env file
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file
load_dotenv()

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)
print(f"\n[INFO] SUPABASE_DB_URL from .env:")
print(f"  {SUPABASE_DB_URL}\n")

# Parse the URL to show details
if SUPABASE_DB_URL:
    parts = SUPABASE_DB_URL.split('@')
    if len(parts) == 2:
        credentials = parts[0].split('://')[-1]
        host_and_db = parts[1]
        username = credentials.split(':')[0]
        host = host_and_db.split(':')[0] if ':' in host_and_db else host_and_db.split('/')[0]
        port = host_and_db.split(':')[1].split('/')[0] if ':' in host_and_db else 'default'
        database = host_and_db.split('/')[-1]
        
        print(f"[INFO] Connection Details:")
        print(f"  Username: {username}")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Database: {database}")
        print()

# Test connection
try:
    print("[TEST] Attempting to connect to database...")
    engine = create_engine(SUPABASE_DB_URL, echo=False)
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        row = result.fetchone()
        print(f"[SUCCESS] ✓ Database connection successful!")
        print(f"[SUCCESS] ✓ Test query returned: {row[0]}")
        
        # Test a real query (table name is 'product' not 'products')
        result = conn.execute(text('SELECT COUNT(*) FROM product'))
        count = result.fetchone()[0]
        print(f"[SUCCESS] ✓ Found {count} products in database")
        
except Exception as e:
    print(f"[ERROR] ✗ Database connection failed!")
    print(f"[ERROR] Error: {e}")
    print()
    print("[INFO] Error details:")
    error_str = str(e)
    if 'pooler.supabase.com' in error_str:
        print("  ⚠ Still trying to connect to POOLER instead of direct connection!")
        print("  ⚠ This means the .env file is not being loaded correctly")
    elif 'no tenant identifier' in error_str:
        print("  ⚠ Missing tenant identifier - wrong connection type")
        print("  ⚠ Should use direct connection (db.*.supabase.co) not pooler")
    elif 'not found' in error_str:
        print("  ⚠ Tenant/user not found - incorrect username format")
    else:
        print(f"  {error_str}")

print("\n" + "=" * 60)
