#!/usr/bin/env python3
"""
Integration test script for mobile app registration and cart functionality.
Tests the complete flow:
1. User registration
2. Admin approval check
3. Login
4. Add to cart
5. Get cart
6. Remove from cart
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://127.0.0.1:5000"  # Use localhost for testing
API_VERSION = "/api/v1"
FULL_API_URL = f"{BASE_URL}{API_VERSION}"

# Test account details
TEST_EMAIL = f"test_buyer_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_PHONE = "+1234567890"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "Buyer"
TEST_COUNTRY = "US"
TEST_CITY = "Test City"

class MobileIntegrationTest:
    def __init__(self):
        self.tokens: Optional[Dict] = None
        self.user_id: Optional[int] = None
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"  {message}")

    def test_connection(self) -> bool:
        """Test if backend is reachable"""
        try:
            response = requests.get(f"{FULL_API_URL}/products", timeout=5)
            self.log_result("Backend Connection", response.status_code == 200)
            return response.status_code == 200
        except Exception as e:
            self.log_result("Backend Connection", False, str(e))
            return False

    def test_register_buyer(self) -> bool:
        """Test buyer registration"""
        try:
            data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "phone": TEST_PHONE,
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "role": "buyer",
                "country": TEST_COUNTRY,
                "city": TEST_CITY
            }
            
            response = requests.post(
                f"{FULL_API_URL}/auth/register",
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                # Extract user ID
                if 'user_id' in result:
                    self.user_id = result['user_id']
                elif 'data' in result and 'id' in result['data']:
                    self.user_id = result['data']['id']
                
                # Check if registration is pending
                message = f"User created with status: {result.get('status', 'unknown')}"
                self.log_result("Register Buyer", True, message)
                return True
            else:
                self.log_result("Register Buyer", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Register Buyer", False, str(e))
            return False

    def test_login_buyer(self) -> bool:
        """Test buyer login with registered account"""
        try:
            data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "role": "buyer"
            }
            
            response = requests.post(
                f"{FULL_API_URL}/auth/login",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract tokens - handle different response formats
                if 'data' in result and 'tokens' in result['data']:
                    self.tokens = result['data']['tokens']
                elif 'tokens' in result:
                    self.tokens = result['tokens']
                else:
                    self.log_result("Login Buyer", False, "No tokens in response")
                    return False
                
                message = f"Login successful with tokens"
                self.log_result("Login Buyer", True, message)
                return True
            else:
                # If login fails, it might be pending approval
                message = f"Status {response.status_code}: {response.text}"
                self.log_result("Login Buyer", False, message)
                return False
        except Exception as e:
            self.log_result("Login Buyer", False, str(e))
            return False

    def test_get_products(self) -> bool:
        """Test getting products"""
        try:
            response = requests.get(
                f"{FULL_API_URL}/products",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                products = result.get('data', result) if isinstance(result, dict) else result
                
                if isinstance(products, list) and len(products) > 0:
                    self.test_product = products[0]
                    message = f"Retrieved {len(products)} products"
                    self.log_result("Get Products", True, message)
                    return True
                else:
                    self.log_result("Get Products", False, "No products returned")
                    return False
            else:
                self.log_result("Get Products", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Products", False, str(e))
            return False

    def test_add_to_cart(self) -> bool:
        """Test adding product to cart"""
        if not self.tokens:
            self.log_result("Add to Cart", False, "No auth tokens available")
            return False
        
        try:
            if not hasattr(self, 'test_product'):
                self.log_result("Add to Cart", False, "No test product available")
                return False
            
            product = self.test_product
            product_id = product.get('id') or product.get('_id')
            
            headers = {
                "Authorization": f"Bearer {self.tokens.get('access_token')}"
            }
            
            data = {
                "product_id": product_id,
                "quantity": 2
            }
            
            response = requests.post(
                f"{FULL_API_URL}/cart/items",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                message = f"Added product {product_id} to cart"
                self.log_result("Add to Cart", True, message)
                return True
            else:
                self.log_result("Add to Cart", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Add to Cart", False, str(e))
            return False

    def test_get_cart(self) -> bool:
        """Test retrieving cart"""
        if not self.tokens:
            self.log_result("Get Cart", False, "No auth tokens available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.tokens.get('access_token')}"
            }
            
            response = requests.get(
                f"{FULL_API_URL}/cart",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                cart = result.get('data', result)
                
                if isinstance(cart, dict):
                    items = cart.get('items', [])
                    message = f"Cart has {len(items)} items"
                elif isinstance(cart, list):
                    message = f"Cart has {len(cart)} items"
                else:
                    message = "Cart retrieved"
                
                self.log_result("Get Cart", True, message)
                return True
            else:
                self.log_result("Get Cart", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Get Cart", False, str(e))
            return False

    def test_remove_from_cart(self) -> bool:
        """Test removing item from cart"""
        if not self.tokens:
            self.log_result("Remove from Cart", False, "No auth tokens available")
            return False
        
        try:
            if not hasattr(self, 'test_product'):
                self.log_result("Remove from Cart", False, "No test product available")
                return False
            
            product_id = self.test_product.get('id') or self.test_product.get('_id')
            
            headers = {
                "Authorization": f"Bearer {self.tokens.get('access_token')}"
            }
            
            response = requests.delete(
                f"{FULL_API_URL}/cart/items/{product_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                message = f"Removed product {product_id} from cart"
                self.log_result("Remove from Cart", True, message)
                return True
            else:
                self.log_result("Remove from Cart", False, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Remove from Cart", False, str(e))
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("MOBILE APP INTEGRATION TEST SUITE")
        print("=" * 60)
        print()
        
        # Basic connectivity
        if not self.test_connection():
            print("\n⚠️  Backend is not reachable. Please start the backend server.")
            print(f"Expected URL: {BASE_URL}")
            print("Cannot proceed with other tests.")
            return False
        
        print()
        
        # Registration flow
        if not self.test_register_buyer():
            print("\n⚠️  Registration failed. Skipping remaining tests.")
            return False
        
        print()
        
        # Login
        if not self.test_login_buyer():
            print("\n⚠️  Login failed. This might be because:")
            print("   - The account is pending admin approval")
            print("   - Invalid credentials")
            print("   Skipping cart tests.")
            login_success = False
        else:
            login_success = True
        
        print()
        
        # Only run cart tests if login succeeded
        if login_success:
            # Get products
            if not self.test_get_products():
                print("\n⚠️  Could not retrieve products. Skipping cart tests.")
                return False
            
            print()
            
            # Cart operations
            self.test_add_to_cart()
            print()
            self.test_get_cart()
            print()
            self.test_remove_from_cart()
        
        # Summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if "PASS" in r["status"])
        total = len(self.test_results)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['message']:
                print(f"    {result['message']}")
        
        print()
        print(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✓ All tests passed!")
        else:
            print(f"✗ {total - passed} test(s) failed")
        
        return passed == total


if __name__ == "__main__":
    tester = MobileIntegrationTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
