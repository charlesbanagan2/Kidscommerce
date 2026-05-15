"""
Test script to verify notification optimizations
Run this after implementing the optimizations to verify performance improvements
"""
import requests
import time
import json
from statistics import mean, median

# Configuration
BASE_URL = "http://localhost:5000"  # Change to your server URL
TEST_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Get from login response

# Test endpoints
ENDPOINTS = {
    "unread_count": "/api/v1/notifications/unread-count",
    "notifications": "/api/v1/notifications?limit=20",
    "notifications_unread": "/api/v1/notifications?unread_only=true&limit=20"
}

def get_headers():
    """Get request headers with auth token"""
    return {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }

def test_endpoint(name, url, iterations=10):
    """Test an endpoint multiple times and return statistics"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}")
    
    times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start = time.time()
            response = requests.get(BASE_URL + url, headers=get_headers(), timeout=10)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                times.append(elapsed)
                status = "✓"
            else:
                errors += 1
                status = "✗"
                print(f"  Request {i+1}: {status} {response.status_code} - {elapsed*1000:.0f}ms")
                continue
            
            # Show progress
            if (i + 1) % 5 == 0 or i == 0:
                print(f"  Request {i+1}: {status} {elapsed*1000:.0f}ms")
                
        except Exception as e:
            errors += 1
            print(f"  Request {i+1}: ✗ Error - {str(e)}")
    
    if times:
        print(f"\n📊 Results:")
        print(f"  Success Rate: {len(times)}/{iterations} ({len(times)/iterations*100:.1f}%)")
        print(f"  Average: {mean(times)*1000:.0f}ms")
        print(f"  Median: {median(times)*1000:.0f}ms")
        print(f"  Min: {min(times)*1000:.0f}ms")
        print(f"  Max: {max(times)*1000:.0f}ms")
        
        # Performance rating
        avg_ms = mean(times) * 1000
        if avg_ms < 100:
            rating = "🚀 EXCELLENT"
        elif avg_ms < 300:
            rating = "✅ GOOD"
        elif avg_ms < 1000:
            rating = "⚠️  ACCEPTABLE"
        else:
            rating = "❌ SLOW"
        
        print(f"  Rating: {rating}")
        
        return {
            'name': name,
            'avg': mean(times) * 1000,
            'median': median(times) * 1000,
            'min': min(times) * 1000,
            'max': max(times) * 1000,
            'success_rate': len(times) / iterations * 100
        }
    else:
        print(f"\n❌ All requests failed!")
        return None

def test_cache_effectiveness():
    """Test if caching is working by making repeated requests"""
    print(f"\n{'='*60}")
    print("Testing Cache Effectiveness")
    print(f"{'='*60}")
    
    url = BASE_URL + ENDPOINTS['unread_count']
    
    # First request (cache miss)
    print("\n1️⃣  First request (cache miss expected):")
    start = time.time()
    response = requests.get(url, headers=get_headers())
    first_time = time.time() - start
    print(f"   Time: {first_time*1000:.0f}ms")
    
    # Immediate second request (cache hit expected)
    print("\n2️⃣  Second request (cache hit expected):")
    start = time.time()
    response = requests.get(url, headers=get_headers())
    second_time = time.time() - start
    print(f"   Time: {second_time*1000:.0f}ms")
    
    # Calculate improvement
    if second_time < first_time:
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"\n✅ Cache is working! {improvement:.1f}% faster on cache hit")
        
        if second_time * 1000 < 50:
            print("   🚀 Excellent cache performance!")
    else:
        print(f"\n⚠️  Cache might not be enabled or working")
        print(f"   Check REDIS_CACHE_ENABLED in .env")

def check_database_indexes():
    """Provide SQL to check if indexes exist"""
    print(f"\n{'='*60}")
    print("Database Index Check")
    print(f"{'='*60}")
    print("\nRun this SQL in Supabase SQL Editor to verify indexes:")
    print("\n" + "="*60)
    print("""
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'notification'
ORDER BY indexname;
    """)
    print("="*60)
    print("\nExpected indexes:")
    print("  - idx_notification_user_id")
    print("  - idx_notification_is_read")
    print("  - idx_notification_created_at")
    print("  - idx_notification_user_unread")
    print("  - idx_notification_user_created")
    print("  - idx_notification_user_type")
    print("  - idx_notification_user_unread_created")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔍 NOTIFICATION API OPTIMIZATION TEST")
    print("="*60)
    
    # Check if token is set
    if TEST_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n❌ ERROR: Please set TEST_TOKEN in the script")
        print("\nTo get a token:")
        print("1. Login via /api/v1/auth/login")
        print("2. Copy the 'access_token' from response")
        print("3. Set TEST_TOKEN in this script")
        return
    
    # Test each endpoint
    results = []
    for name, endpoint in ENDPOINTS.items():
        result = test_endpoint(name, endpoint, iterations=10)
        if result:
            results.append(result)
        time.sleep(1)  # Brief pause between tests
    
    # Test cache effectiveness
    test_cache_effectiveness()
    
    # Show database index check instructions
    check_database_indexes()
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print(f"{'='*60}")
    
    if results:
        print("\nEndpoint Performance:")
        for result in results:
            print(f"\n  {result['name']}:")
            print(f"    Average: {result['avg']:.0f}ms")
            print(f"    Success: {result['success_rate']:.1f}%")
    
    print("\n✅ Optimization Checklist:")
    print("  [ ] Database indexes created in Supabase")
    print("  [ ] Redis cache enabled (optional)")
    print("  [ ] All endpoints responding under 300ms")
    print("  [ ] Cache hit rate > 80% (if enabled)")
    
    print("\n📚 See OPTIMIZATION_GUIDE.md for detailed setup instructions")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
