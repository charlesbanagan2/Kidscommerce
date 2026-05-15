import requests
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Test configuration
BASE_URL = "http://localhost:5000"
DB_URL = "postgresql+psycopg2://postgres:Kidscommerce%401234@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres"

print("=" * 80)
print("LIVE PERFORMANCE TEST - Testing Running Flask Server")
print("=" * 80)

# Test 1: Direct Database Connection Speed
print("\n[TEST 1] Direct Database Connection Speed")
print("-" * 80)
try:
    engine = create_engine(DB_URL, pool_pre_ping=True, connect_args={'connect_timeout': 5})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    start = time.time()
    result = session.execute(text("SELECT 1")).fetchone()
    db_time = (time.time() - start) * 1000
    print(f"✓ Database ping: {db_time:.0f}ms")
    
    start = time.time()
    result = session.execute(text("SELECT COUNT(*) FROM product WHERE status='active'")).fetchone()
    count_time = (time.time() - start) * 1000
    print(f"✓ Product count query: {count_time:.0f}ms (Found {result[0]} products)")
    
    session.close()
except Exception as e:
    print(f"✗ Database test failed: {e}")

# Test 2: Flask Server Response Times
print("\n[TEST 2] Flask Server HTTP Response Times")
print("-" * 80)

endpoints = [
    ("/", "Homepage"),
    ("/shop", "Shop Page"),
    ("/login", "Login Page"),
]

for endpoint, name in endpoints:
    try:
        start = time.time()
        response = requests.get(BASE_URL + endpoint, timeout=10)
        response_time = (time.time() - start) * 1000
        
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {name}: {response_time:.0f}ms (Status: {response.status_code})")
        
        # Check if response contains expected content
        if endpoint == "/" and "product" in response.text.lower():
            print(f"  → Contains product data")
        
    except requests.exceptions.Timeout:
        print(f"✗ {name}: TIMEOUT (>10 seconds)")
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")

# Test 3: Check if server is using optimizations
print("\n[TEST 3] Server Configuration Check")
print("-" * 80)
try:
    # Test if server responds quickly to static content
    start = time.time()
    response = requests.get(BASE_URL + "/static/css/style.css", timeout=5)
    static_time = (time.time() - start) * 1000
    print(f"✓ Static file serving: {static_time:.0f}ms")
    
    # Test homepage multiple times to check caching/pooling
    times = []
    for i in range(3):
        start = time.time()
        response = requests.get(BASE_URL + "/", timeout=10)
        times.append((time.time() - start) * 1000)
    
    print(f"\n✓ Homepage load times (3 requests):")
    for i, t in enumerate(times, 1):
        print(f"  Request {i}: {t:.0f}ms")
    
    avg_time = sum(times) / len(times)
    print(f"  Average: {avg_time:.0f}ms")
    
    if avg_time < 500:
        print("  ✓ GOOD - Server is fast!")
    elif avg_time < 1500:
        print("  ⚠ MODERATE - Could be better")
    else:
        print("  ✗ SLOW - Performance issue detected")
        
except Exception as e:
    print(f"✗ Configuration check failed: {e}")

# Test 4: Database Query Analysis
print("\n[TEST 4] Database Query Performance")
print("-" * 80)
try:
    session = Session()
    
    # Test query with eager loading (what should be happening)
    from sqlalchemy.orm import joinedload
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String, Float, ForeignKey
    
    Base = declarative_base()
    
    class Product(Base):
        __tablename__ = 'product'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        price = Column(Float)
        seller_id = Column(Integer, ForeignKey('user.id'))
        category_id = Column(Integer, ForeignKey('category.id'))
    
    start = time.time()
    products = session.query(Product).filter_by(status='active').limit(24).all()
    query_time = (time.time() - start) * 1000
    print(f"✓ Products query (no eager loading): {query_time:.0f}ms")
    
    session.close()
    
except Exception as e:
    print(f"⚠ Query analysis: {e}")

# Test 5: Network Latency to Supabase
print("\n[TEST 5] Network Latency Analysis")
print("-" * 80)
try:
    import socket
    
    host = "db.qkdacoawexaxejljfihh.supabase.co"
    port = 6543
    
    latencies = []
    for i in range(5):
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        sock.close()
        latency = (time.time() - start) * 1000
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    
    print(f"✓ Network latency to Supabase:")
    print(f"  Min: {min_latency:.0f}ms")
    print(f"  Max: {max_latency:.0f}ms")
    print(f"  Avg: {avg_latency:.0f}ms")
    
    if avg_latency < 100:
        print("  ✓ EXCELLENT - Low latency")
    elif avg_latency < 300:
        print("  ✓ GOOD - Acceptable latency")
    elif avg_latency < 500:
        print("  ⚠ MODERATE - Higher than expected")
    else:
        print("  ✗ HIGH - Network latency is a problem")
        
except Exception as e:
    print(f"✗ Network test failed: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS SUMMARY")
print("=" * 80)
print("\nIf homepage is still >2 seconds:")
print("1. Check if Flask server was ACTUALLY restarted (not just code saved)")
print("2. Check Flask console for SQL query logs - should see 1 query, not 49")
print("3. Network latency >500ms means Supabase connection is the bottleneck")
print("4. Try accessing from incognito/private browser window")
print("\nNext steps based on results above:")
print("- If DB queries are fast but HTTP is slow → Flask app issue")
print("- If DB queries are slow → Network/Supabase issue")
print("- If static files are slow → Server/network issue")
print("=" * 80)
