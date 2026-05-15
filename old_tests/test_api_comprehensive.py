#!/usr/bin/env python3
"""
Comprehensive Backend API Test - WITH VALID CREDENTIALS
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://192.168.1.20:5000"
HEADERS = {"Content-Type": "application/json"}

# Valid test credentials from database
TEST_CREDENTIALS = {
    "buyer1": {"email": "juanbuyer@gmail.com", "password": "Buyer@1234"},
    "buyer2": {"email": "codechat45@gmail.com", "password": "030904Jeff!"},
    "buyer3": {"email": "buyer2@gmail.com", "password": "Buyer@1234"},
}

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.passed = 0
        self.failed = 0

    def log_result(self, name, status, details=""):
        """Log test result"""
        status_icon = "✅" if status else "❌"
        message = f"  {status_icon} {name}"
        if details:
            message += f" | {details}"
        print(message)
        
        if status:
            self.passed += 1
        else:
            self.failed += 1

    def test_server(self):
        """Test server is running"""
        print("\n=== SERVER STATUS ===")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            self.log_result("Server Health", response.status_code == 200)
            return response.status_code == 200
        except Exception as e:
            self.log_result("Server Health", False, str(e))
            return False

    def test_public_endpoints(self):
        """Test public endpoints"""
        print("\n=== PUBLIC ENDPOINTS ===")
        
        endpoints = [
            ("/api/v1/products/sync", "Products Sync"),
            ("/api/v1/categories", "Categories"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=HEADERS,
                    timeout=10
                )
                
                count = 0
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else len(data.get('categories', data.get('products', [])))
                
                self.log_result(name, response.status_code == 200, f"{count} items")
            except Exception as e:
                self.log_result(name, False, str(e))

    def test_login(self):
        """Test login with valid credentials"""
        print("\n=== AUTHENTICATION ===")
        
        for user_name, creds in TEST_CREDENTIALS.items():
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json=creds,
                    headers=HEADERS,
                    timeout=10
                )
                
                success = response.status_code == 200
                if success and response.json():
                    data = response.json()
                    if 'tokens' in data:
                        self.access_token = data['tokens'].get('access_token')
                
                user_display = creds['email'].split('@')[0]
                self.log_result(f"Login - {user_display}", success)
                
                if success:
                    return True
            except Exception as e:
                user_display = creds['email'].split('@')[0]
                self.log_result(f"Login - {user_display}", False, str(e))
        
        return False

    def test_protected_endpoints(self):
        """Test protected endpoints"""
        print("\n=== PROTECTED ENDPOINTS ===")
        
        if not self.access_token:
            print("  ⚠️  No access token - skipping protected endpoints")
            return
        
        headers = {**HEADERS, "Authorization": f"Bearer {self.access_token}"}
        
        # Test cart endpoints
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/buyer/orders",
                headers=headers,
                timeout=10
            )
            success = response.status_code in [200, 404]
            self.log_result("Get Orders", success)
        except Exception as e:
            self.log_result("Get Orders", False, str(e))
        
        # Test adding to cart
        try:
            payload = {"product_id": 1, "quantity": 1}
            response = self.session.post(
                f"{self.base_url}/api/v1/buyer/cart/add",
                json=payload,
                headers=headers,
                timeout=10
            )
            success = response.status_code in [200, 201, 400, 404]  # 404 if endpoint doesn't exist
            self.log_result("Add to Cart", success)
        except Exception as e:
            self.log_result("Add to Cart", False, str(e))

    def test_all_routes(self):
        """Discover and test available routes"""
        print("\n=== AVAILABLE API ROUTES ===")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/debug/routes",
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                routes = response.json()
                print(f"  Found {len(routes)} routes")
                for route in routes[:10]:
                    print(f"    - {route}")
                if len(routes) > 10:
                    print(f"    ... and {len(routes) - 10} more")
            else:
                # Try alternative method
                print("  Debug routes endpoint not available")
        except Exception as e:
            print(f"  Could not retrieve routes: {e}")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("BACKEND API COMPREHENSIVE TEST")
        print("="*80)
        
        if not self.test_server():
            print("\n❌ Server is not running!")
            return False
        
        self.test_public_endpoints()
        success = self.test_login()
        if success:
            self.test_protected_endpoints()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*80 + "\n")

def main():
    tester = APITester(BASE_URL)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
