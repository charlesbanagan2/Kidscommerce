#!/usr/bin/env python3
"""
Switch from Supabase to SQLite for local development
This creates a local database file that works without internet
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("SWITCH TO SQLITE DATABASE")
print("=" * 80)
print()

# Path to .env file
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
env_file = os.path.join(backend_dir, '.env')

print(f"[1] Creating backup of current .env...")
try:
    with open(env_file, 'r') as f:
        original_content = f.read()
    
    backup_file = os.path.join(backend_dir, '.env.supabase.backup')
    with open(backup_file, 'w') as f:
        f.write(original_content)
    print(f"    ✓ Backup saved to: {backup_file}")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

print()
print(f"[2] Updating .env to use SQLite...")

# Read current .env
try:
    with open(env_file, 'r') as f:
        lines = f.readlines()
except Exception as e:
    print(f"    ✗ Error reading .env: {e}")
    sys.exit(1)

# Replace database configuration
new_lines = []
for line in lines:
    # Replace Supabase settings with SQLite
    if line.startswith('SUPABASE_DB_URL'):
        new_lines.append('SUPABASE_DB_URL=sqlite:///kids_commerce.db\n')
        new_lines.append('# Switched to SQLite for local development\n')
    elif line.startswith('SQLALCHEMY_DATABASE_URI'):
        new_lines.append('SQLALCHEMY_DATABASE_URI=sqlite:///kids_commerce.db\n')
    else:
        new_lines.append(line)

# Write updated .env
try:
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    print(f"    ✓ .env updated to use SQLite")
except Exception as e:
    print(f"    ✗ Error writing .env: {e}")
    sys.exit(1)

print()
print("[3] SQLite Setup Complete!")
print("-" * 80)
print()
print("✓ Your app will now use SQLite database: kids_commerce.db")
print()
print("Next steps:")
print("1. Start your Flask app:")
print("   cd backend")
print("   python app.py")
print()
print("2. The database file will be created automatically when app starts")
print()
print("Important:")
print("- ⚠ SQLite is for DEVELOPMENT ONLY")
print("- ⚠ Do NOT use this for production")
print("- ⚠ To go back to Supabase when it's fixed:")
print("   cp backend/.env.supabase.backup backend/.env")
print()
print("=" * 80)
