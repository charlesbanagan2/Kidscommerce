#!/usr/bin/env python3
"""
Quick setup script for local PostgreSQL database
Run this to configure your local database for development
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    print("=" * 70)
    print("PostgreSQL Setup for Kids Commerce Development")
    print("=" * 70)
    
    # Check if PostgreSQL is installed
    print("\n📋 Checking for PostgreSQL installation...")
    code, out, err = run_command("psql --version", check=False)
    
    if code != 0:
        print("❌ PostgreSQL not found!")
        print("\n📥 Installation Instructions:")
        print("""
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer (choose default settings)
3. Remember your password for the 'postgres' user
4. After installation, run this script again
        """)
        return False
    
    print(f"✅ PostgreSQL is installed: {out.strip()}")
    
    # Get password
    print("\n🔑 Enter PostgreSQL password for 'postgres' user:")
    password = input("Password: ").strip()
    
    if not password:
        print("❌ Password required!")
        return False
    
    # Test connection
    print("\n🧪 Testing connection...")
    code, out, err = run_command(
        f'psql -U postgres -c "SELECT 1" -h localhost',
        check=False
    )
    
    if code != 0:
        print(f"❌ Connection failed: {err}")
        print("\nMake sure PostgreSQL service is running:")
        print("  1. Open Services (services.msc)")
        print("  2. Find 'PostgreSQL Database Server'")
        print("  3. Check if status is 'Running'")
        return False
    
    print("✅ Connection successful!")
    
    # Create database
    db_name = "kids_commerce_dev"
    print(f"\n📊 Creating database '{db_name}'...")
    
    code, out, err = run_command(
        f'psql -U postgres -c "CREATE DATABASE {db_name};" -h localhost',
        check=False
    )
    
    if code == 0:
        print(f"✅ Database '{db_name}' created!")
    elif "already exists" in err:
        print(f"⚠️  Database '{db_name}' already exists (that's OK!)")
    else:
        print(f"❌ Failed to create database: {err}")
        return False
    
    # Update .env file
    print("\n📝 Updating .env file...")
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        return False
    
    env_content = env_path.read_text()
    
    # Update database configuration
    old_db_lines = [
        'SUPABASE_DB_URL=',
        'SUPABASE_DB_HOST=',
        'SUPABASE_DB_PORT=',
        'SUPABASE_DB_USER=',
        'SUPABASE_DB_PASSWORD=',
        'SUPABASE_DB_NAME=',
    ]
    
    # Filter out old database lines
    lines = env_content.split('\n')
    new_lines = [line for line in lines if not any(line.startswith(old) for old in old_db_lines)]
    
    # Add new configuration
    new_lines.insert(0, f'SUPABASE_DB_PASSWORD={password}')
    new_lines.insert(0, 'SUPABASE_DB_USER=postgres')
    new_lines.insert(0, 'SUPABASE_DB_NAME=kids_commerce_dev')
    new_lines.insert(0, 'SUPABASE_DB_PORT=5432')
    new_lines.insert(0, 'SUPABASE_DB_HOST=localhost')
    new_lines.insert(0, 'SUPABASE_DB_URL=postgresql+psycopg2://postgres:{password}@localhost:5432/kids_commerce_dev'.format(
        password=password.replace('@', '%40')
    ))
    
    new_env_content = '\n'.join(new_lines)
    env_path.write_text(new_env_content)
    
    print("✅ .env file updated!")
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("""
Your Flask app can now connect to the local PostgreSQL database.

Next steps:
1. Start your Flask app: python app.py
2. Visit: http://localhost:5000/
3. If you need to reset the database, run:
   psql -U postgres -c "DROP DATABASE kids_commerce_dev;" -h localhost
   psql -U postgres -c "CREATE DATABASE kids_commerce_dev;" -h localhost
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
