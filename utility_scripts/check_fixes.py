import re

# Check if fixes are applied in app.py
with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
print("=== CHECKING APPLIED FIXES ===\n")

# Check 1: Connection pool settings
if 'pool_size=20' in content:
    print("✓ Connection pool optimized (pool_size=20)")
else:
    print("✗ Connection pool NOT optimized")

# Check 2: Eager loading in index route
if 'joinedload(Product.seller)' in content and 'joinedload(Product.category)' in content:
    print("✓ Eager loading applied (joinedload)")
else:
    print("✗ Eager loading NOT applied")

# Check 3: SUPABASE_DB_URL in env file
with open('mobile_app/lib/kids_commercedb/supabase.env', 'r') as f:
    env_content = f.read()
    if 'SUPABASE_DB_URL=postgresql' in env_content:
        print("✓ SUPABASE_DB_URL configured")
    else:
        print("✗ SUPABASE_DB_URL empty")

print("\n=== NEXT STEPS ===")
print("1. Restart Flask server: Ctrl+C then run again")
print("2. Clear browser cache")
print("3. Test homepage loading speed")
