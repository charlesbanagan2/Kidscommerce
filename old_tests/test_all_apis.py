#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all critical endpoints for the Kids eCommerce Mobile App
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://192.168.1.20:5000"
HEADERS = {"Content-Type": "application/json"}

# Test data
TEST_EMAIL = "buyer@example.com"
TEST_PASSWORD = "password123"

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.passed = 0
        self.failed = 0
        self.results = []

    def log_test(self, name, status, details=""):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status else "❌"
        message = f"[{timestamp}] {status_icon} {name}"
        if details:
            message += f" | {details}"
        print(message)
        self.results.append({"test": name, "status": status, "details": details})
        
        if status:
            self.passed += 1
        else:
            self.failed += 1

    def test_server_health(self):
        """Test if server is running"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            self.log_test("Server Health Check", response.status_code == 200, f"Status: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError:
            self.log_test("Server Health Check", False, "Cannot connect to server")
            return False
        except Exception as e:
            self.log_test("Server Health Check", False, str(e))
            return False

    def test_auth_login(self):
        """Test user login"""
        try:
            payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=payload,
                headers=HEADERS,
                timeout=10
            )
            
            success = response.status_code == 200
            if success and response.json():
                data = response.json()
                if 'tokens' in data:
                    self.access_token = data['tokens'].get('access_token')
                    self.refresh_token = data['tokens'].get('refresh_token')
                elif 'access_token' in data:
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
            
            self.log_test("Auth - Login", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Auth - Login", False, str(e))
            return False

    def test_products_sync(self):
        """Test product synchronization endpoint"""
        try:
            headers = {**HEADERS}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            response = self.session.get(
                f"{self.base_url}/api/v1/products/sync",
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            product_count = 0
            if success and response.json():
                data = response.json()
                if isinstance(data, list):
                    product_count = len(data)
                elif 'products' in data:
                    product_count = len(data['products'])
            
            self.log_test("Products - Sync", success, f"Status: {response.status_code}, Products: {product_count}")
            return success
        except Exception as e:
            self.log_test("Products - Sync", False, str(e))
            return False

    def test_cart_add(self):
        """Test add to cart endpoint"""
        try:
            if not self.access_token:
                self.log_test("Cart - Add Product", False, "No access token")
                return False
            
            headers = {**HEADERS, "Authorization": f"Bearer {self.access_token}"}
            payload = {
                "product_id": 1,
                "quantity": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/buyer/cart/add",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            success = response.status_code in [200, 201]
            self.log_test("Cart - Add Product", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Cart - Add Product", False, str(e))
            return False

    def test_cart_get(self):
        """Test get cart endpoint"""
        try:
            if not self.access_token:
                self.log_test("Cart - Get Cart", False, "No access token")
                return False
            
            headers = {**HEADERS, "Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(
                f"{self.base_url}/api/v1/buyer/cart",
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            cart_items = 0
            if success and response.json():
                data = response.json()
                if isinstance(data, list):
                    cart_items = len(data)
                elif 'items' in data:
                    cart_items = len(data['items'])
            
            self.log_test("Cart - Get Cart", success, f"Status: {response.status_code}, Items: {cart_items}")
            return success
        except Exception as e:
            self.log_test("Cart - Get Cart", False, str(e))
            return False

    def test_orders_by_status(self):
        """Test get orders by status endpoint"""
        try:
            if not self.access_token:
                self.log_test("Orders - By Status", False, "No access token")
                return False
            
            headers = {**HEADERS, "Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(
                f"{self.base_url}/api/v1/buyer/orders/by-status?status=pending",
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            order_count = 0
            if success and response.json():
                data = response.json()
                if isinstance(data, list):
                    order_count = len(data)
                elif 'orders' in data:
                    order_count = len(data['orders'])
            
            self.log_test("Orders - By Status", success, f"Status: {response.status_code}, Orders: {order_count}")
            return success
        except Exception as e:
            self.log_test("Orders - By Status", False, str(e))
            return False

    def test_categories(self):
        """Test get categories endpoint"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/categories",
                headers=HEADERS,
                timeout=10
            )
            
            success = response.status_code == 200
            category_count = 0
            if success and response.json():
                data = response.json()
                if isinstance(data, list):
                    category_count = len(data)
                elif 'categories' in data:
                    category_count = len(data['categories'])
            
            self.log_test("Categories - Get All", success, f"Status: {response.status_code}, Categories: {category_count}")
            return success
        except Exception as e:
            self.log_test("Categories - Get All", False, str(e))
            return False

    def test_database_connection(self):
        """Test database connectivity through a simple endpoint"""
        try:
            # This will indirectly test database
            response = self.session.get(
                f"{self.base_url}/api/v1/products/sync?page=1&per_page=1",
                headers=HEADERS,
                timeout=10
            )
            
            success = response.status_code == 200
            self.log_test("Database - Connection", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Database - Connection", False, str(e))
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("BACKEND API COMPREHENSIVE TEST SUITE")
        print("="*80 + "\n")
        
        # Check server first
        if not self.test_server_health():
            print("\n❌ Server is not running! Cannot continue tests.")
            return False
        
        print("\n--- Authentication Tests ---")
        self.test_auth_login()
        
        print("\n--- Product Tests ---")
        self.test_products_sync()
        self.test_categories()
        
        print("\n--- Cart Tests ---")
        self.test_cart_add()
        self.test_cart_get()
        
        print("\n--- Order Tests ---")
        self.test_orders_by_status()
        
        print("\n--- Database Tests ---")
        self.test_database_connection()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "N/A")
        print("="*80 + "\n")
        
        return self.failed == 0

def main():
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
