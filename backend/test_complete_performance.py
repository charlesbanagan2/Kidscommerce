# ⚡ COMPLETE PERFORMANCE TEST SUITE
# Tests all optimized endpoints and measures performance

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "juanbuyer@gmail.com"
TEST_PASSWORD = "Juan123!"

class PerformanceTest:
    def __init__(self):
        self.token = None
        self.results = []
    
    def login(self):
        """Login and get token"""
        print("\n🔐 Logging in...")
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access_token')
            print(f"✅ Login successful! Token: {self.token[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def test_endpoint(self, name, method, url, **kwargs):
        """Test an endpoint and measure performance"""
        print(f"\n📊 Testing: {name}")
        print(f"   URL: {url}")
        
        headers = kwargs.get('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        start = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, **kwargs)
            elif method == 'POST':
                response = requests.post(url, **kwargs)
            else:
                response = requests.request(method, url, **kwargs)
            
            elapsed = time.time() - start
            
            result = {
                'name': name,
                'url': url,
                'method': method,
                'status': response.status_code,
                'time': elapsed,
                'success': response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['data_size'] = len(json.dumps(data))
                    result['performance'] = data.get('performance', {})
                except:
                    pass
            
            self.results.append(result)
            
            # Print result
            status_icon = "✅" if result['success'] else "❌"
            time_color = "🟢" if elapsed < 1 else "🟡" if elapsed < 2 else "🔴"
            
            print(f"   {status_icon} Status: {response.status_code}")
            print(f"   {time_color} Time: {elapsed:.3f}s")
            
            if result.get('performance'):
                perf = result['performance']
                print(f"   📈 Queries: {perf.get('queries', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {
                'name': name,
                'url': url,
                'method': method,
                'error': str(e),
                'success': False
            }
    
    def run_all_tests(self):
        """Run all performance tests"""
        print("\n" + "="*60)
        print("⚡ STARTING COMPLETE PERFORMANCE TEST SUITE")
        print("="*60)
        
        # Login first
        if not self.login():
            print("\n❌ Cannot proceed without login")
            return
        
        # Test 1: Orders (should be 1-2s)
        self.test_endpoint(
            "Get User Orders",
            "GET",
            f"{BASE_URL}/api/v1/orders/user"
        )
        
        # Test 2: Cart (should be 0.5-1s)
        self.test_endpoint(
            "Get Cart",
            "GET",
            f"{BASE_URL}/api/v1/cart"
        )
        
        # Test 3: Products (should be 1-2s)
        self.test_endpoint(
            "Get Products (Page 1)",
            "GET",
            f"{BASE_URL}/api/v1/products?page=1&per_page=20"
        )
        
        # Test 4: Notifications (should be 0.5-1s)
        self.test_endpoint(
            "Get Notifications",
            "GET",
            f"{BASE_URL}/api/v1/notifications?page=1&per_page=20"
        )
        
        # Test 5: Product Detail (should be <1s)
        self.test_endpoint(
            "Get Product Detail",
            "GET",
            f"{BASE_URL}/api/v1/products/1"
        )
        
        # Test 6: Categories (should be <0.5s)
        self.test_endpoint(
            "Get Categories",
            "GET",
            f"{BASE_URL}/api/v1/categories"
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        print(f"\n✅ Successful: {len(successful)}/{len(self.results)}")
        print(f"❌ Failed: {len(failed)}/{len(self.results)}")
        
        if successful:
            times = [r['time'] for r in successful]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            print(f"\n⏱️  Response Times:")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Fastest: {min_time:.3f}s")
            print(f"   Slowest: {max_time:.3f}s")
        
        # Performance grades
        print(f"\n🎯 Performance Grades:")
        for result in successful:
            time_val = result['time']
            if time_val < 0.5:
                grade = "⚡ EXCELLENT"
            elif time_val < 1.0:
                grade = "🟢 GOOD"
            elif time_val < 2.0:
                grade = "🟡 ACCEPTABLE"
            else:
                grade = "🔴 NEEDS IMPROVEMENT"
            
            print(f"   {result['name']}: {time_val:.3f}s - {grade}")
        
        # Failed tests
        if failed:
            print(f"\n❌ Failed Tests:")
            for result in failed:
                print(f"   {result['name']}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60)
        print("✅ TEST SUITE COMPLETE!")
        print("="*60)

if __name__ == "__main__":
    tester = PerformanceTest()
    tester.run_all_tests()
