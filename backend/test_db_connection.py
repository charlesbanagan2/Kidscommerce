import os
import socket
import psycopg2
from dotenv import load_dotenv

# Load environment variables
SUPABASE_ENV_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'mobile_app',
    'lib',
    'kids_commercedb',
    'supabase.env',
)
load_dotenv(SUPABASE_ENV_PATH, override=True)

# Get connection parameters
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip()
db_host = os.getenv('SUPABASE_DB_HOST', '')
db_port = os.getenv('SUPABASE_DB_PORT', '6543')
db_user = os.getenv('SUPABASE_DB_USER', '')
db_password = os.getenv('SUPABASE_DB_PASSWORD', '')
db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')

print("=" * 80)
print("Database Connection Diagnostic")
print("=" * 80)
print(f"\nSUPABASE_DB_URL: {SUPABASE_DB_URL[:50]}..." if SUPABASE_DB_URL else "SUPABASE_DB_URL: Not set")
print(f"DB Host: {db_host}")
print(f"DB Port: {db_port}")
print(f"DB User: {db_user}")
print(f"DB Name: {db_name}")

# Test 1: DNS resolution
print("\n" + "=" * 80)
print("Test 1: DNS Resolution")
print("=" * 80)
try:
    ip_address = socket.gethostbyname(db_host)
    print(f"✓ DNS resolved: {db_host} -> {ip_address}")
except socket.gaierror as e:
    print(f"✗ DNS resolution failed: {e}")
    exit(1)

# Test 2: TCP connection test
print("\n" + "=" * 80)
print("Test 2: TCP Connection Test")
print("=" * 80)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  # 10 second timeout
    result = sock.connect_ex((db_host, int(db_port)))
    sock.close()
    if result == 0:
        print(f"✓ TCP connection successful to {db_host}:{db_port}")
    else:
        print(f"✗ TCP connection failed to {db_host}:{db_port} (error code: {result})")
        exit(1)
except Exception as e:
    print(f"✗ TCP connection error: {e}")
    exit(1)

# Test 3: PostgreSQL connection with longer timeout
print("\n" + "=" * 80)
print("Test 3: PostgreSQL Connection Test")
print("=" * 80)
try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        connect_timeout=10  # 10 second timeout
    )
    print("✓ PostgreSQL connection successful!")
    conn.close()
except psycopg2.OperationalError as e:
    print(f"✗ PostgreSQL connection failed: {e}")
    print("\nPossible causes:")
    print("  1. Network firewall blocking port 6543")
    print("  2. VPN or proxy interference")
    print("  3. Supabase database paused or down")
    print("  4. Incorrect credentials")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)

print("\n" + "=" * 80)
print("All tests passed!")
print("=" * 80)
