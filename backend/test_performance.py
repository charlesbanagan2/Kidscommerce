"""
Simple Performance Test - Measure actual route performance
"""
import time
import requests

BASE_URL = "http://localhost:5000"

def test_route(route_name, url):
    """Test a single route and measure response time"""
    print(f"\n📊 Testing: {route_name}")
    print(f"   URL: {url}")
    
    times = []
    for i in range(3):
        start = time.time()
        try:
            response = requests.get(url, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            
            status = "✓" if response.status_code == 200 else "✗"
            print(f"   Attempt {i+1}: {status} {elapsed:.2f}s (status: {response.status_code})")
        except Exception as e:
            print(f"   Attempt {i+1}: ✗ Error - {str(e)[:50]}")
            times.append(999)
    
    avg_time = sum(times) / len(times)
    print(f"   Average: {avg_time:.2f}s")
    
    if avg_time > 2.0:
        print(f"   ⚠️  VERY SLOW - Should be < 1s")
    elif avg_time > 1.0:
        print(f"   ⚠️  SLOW - Should be < 1s")
    else:
        print(f"   ✓ Good performance")
    
    return avg_time

def main():
    print("="*60)
    print("REAL-WORLD PERFORMANCE TEST")
    print("="*60)
    print("\nMake sure your Flask server is running on http://localhost:5000")
    print("Testing actual page load times...\n")
    
    # Test routes
    routes = [
        ("Homepage", f"{BASE_URL}/"),
        ("Shop/Products", f"{BASE_URL}/shop"),
        ("Login Page", f"{BASE_URL}/login"),
    ]
    
    results = {}
    for name, url in routes:
        results[name] = test_route(name, url)
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total_avg = sum(results.values()) / len(results)
    print(f"\nOverall average: {total_avg:.2f}s")
    
    print("\nSlowest routes:")
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    for name, time_taken in sorted_results[:3]:
        print(f"   {name}: {time_taken:.2f}s")
    
    print("\n" + "="*60)
    print("DIAGNOSIS")
    print("="*60)
    
    if total_avg > 2.0:
        print("\n⚠️  CRITICAL: Very slow performance detected")
        print("\nMost likely causes:")
        print("1. N+1 Query Problem (most common)")
        print("   → Each product loads seller/category separately")
        print("   → Fix: Add joinedload() to queries")
        print("\n2. Network latency to Supabase")
        print("   → Check Supabase region in dashboard")
        print("   → Verify using pooled connection (:6543)")
        print("\n3. Large dataset without pagination")
        print("   → Add .limit() to queries")
        
    elif total_avg > 1.0:
        print("\n⚠️  Moderate slowness detected")
        print("\nRecommended fixes:")
        print("1. Add eager loading (joinedload) to queries")
        print("2. Add pagination to large lists")
        print("3. Consider caching frequently accessed pages")
        
    else:
        print("\n✓ Performance is acceptable")
        print("\nOptional improvements:")
        print("1. Add caching for even faster loads")
        print("2. Optimize images (compress, use WebP)")
        print("3. Add CDN for static assets")
    
    print("\n" + "="*60)
    print("\nNext steps:")
    print("1. Check FIX_N_PLUS_1.md for query optimization")
    print("2. Add logging to see query counts per request")
    print("3. Profile specific slow routes")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("1. Flask server is running (python app.py)")
        print("2. Server is accessible at http://localhost:5000")
        print("3. requests library is installed (pip install requests)")
