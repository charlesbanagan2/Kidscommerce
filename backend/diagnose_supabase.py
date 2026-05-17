#!/usr/bin/env python3
"""
Diagnostic script to check Supabase database connection and configuration
"""

import os
import socket
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment
load_dotenv('.env')

def check_dns_resolution(hostname):
    """Check if hostname can be resolved"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS Resolution: SUCCESS - {hostname} → {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS Resolution: FAILED - {hostname}")
        print(f"   Error: {e}")
        return False

def check_port_connectivity(hostname, port):
    """Check if port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port Connectivity: SUCCESS - {hostname}:{port} is accessible")
            return True
        else:
            print(f"❌ Port Connectivity: FAILED - {hostname}:{port} is not accessible")
            return False
    except Exception as e:
        print(f"❌ Port Connectivity: FAILED - {e}")
        return False

def main():
    print("=" * 60)
    print("Supabase Connection Diagnostic")
    print("=" * 60)
    
    # Get configuration
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_port = os.getenv('SUPABASE_DB_PORT', '6543')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_name = os.getenv('SUPABASE_DB_NAME')
    db_url = os.getenv('SUPABASE_DB_URL')
    
    print("\n📋 Configuration:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  User: {db_user}")
    print(f"  Database: {db_name}")
    print(f"  URL: {db_url[:50]}..." if db_url else "  URL: Not set")
    
    # Check DNS
    print("\n🔍 Network Checks:")
    dns_ok = check_dns_resolution(db_host)
    
    if dns_ok:
        port_ok = check_port_connectivity(db_host, int(db_port))
    else:
        port_ok = False
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not dns_ok:
        print("""
The Supabase hostname cannot be resolved. This usually means:

1. **Supabase Project Deleted/Inactive**: Check your Supabase dashboard
   - Log in at https://app.supabase.com
   - Verify your project exists and is active
   - Get the correct database host from Project Settings → Database

2. **Wrong Hostname**: The hostname in .env might be incorrect
   - Copy the correct connection string from Supabase dashboard
   - Update SUPABASE_DB_URL in .env with the new credentials

3. **Network/Firewall Issue**: Your network might be blocking connections
   - Try on a different network (mobile hotspot)
   - Check if your VPN is interfering

For Development (Recommended):
   Consider using a local PostgreSQL database instead:
   
   a) Install PostgreSQL locally
   b) Create a local database: createdb kids_commerce_dev
   c) Update .env:
      SUPABASE_DB_HOST=localhost
      SUPABASE_DB_PORT=5432
      SUPABASE_DB_USER=postgres
      SUPABASE_DB_PASSWORD=your_password
      SUPABASE_DB_NAME=kids_commerce_dev
        """)
    elif not port_ok:
        print("""
The hostname resolves but the port is not accessible.
This usually means:

1. The Supabase project is inactive
2. Your firewall is blocking the connection
3. The port number is wrong

Try:
   - Check that the Supabase project is running
   - Verify the port is correct (usually 6543 for Supabase)
   - Disable any VPN or firewall temporarily to test
        """)
    else:
        print("✅ Network connectivity looks good!")
        print("The database connection should work. If you're still getting errors,")
        print("check that your credentials (password, user) are correct.")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error running diagnostic: {e}")
        sys.exit(1)
