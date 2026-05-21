"""
Automated Wishlist API Test Script
Tests wishlist persistence across login/logout sessions
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Change to your backend URL
TEST_EMAIL = "buyer@test.com"
TEST_PASSWORD = "password123"  # Change to actual test password

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class WishlistTester:
    def __init__(self):
        self.access_token = None
        self.test_results = []
        self.test_product_ids = []
        
    def log(self, message, color=RESET):
        """Print colored log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{RESET}")
        
    def test_result(self, test_name, passed, message=""):
        """Record test result"""
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        self.log(f"{test_name}: {status} {message}", GREEN if passed else RED)
        
    def login(self):
        """Login and get access token"""
        self.log("🔐 Logging in...", BLUE)
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                if self.access_token:
                    self.log(f"✅ Login successful", GREEN)
                    return True
                else:
                    self.log(f"❌ No access token in response", RED)
                    return False
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}", RED)
                return False
        except Exception as e:
            self.log(f"❌ Login error: {e}", RED)
            return False
            
    def logout(self):
        """Simulate logout by clearing token"""
        self.log("🚪 Logging out (clearing token)...", BLUE)
        self.access_token = None
        time.sleep(1)  # Simulate time between sessions
        
    def get_headers(self):
        """Get request headers with auth token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
    def get_products(self):
        """Get list of products to test with"""
        self.log("📦 Fetching products...", BLUE)
        try:
            response = requests.get(f"{BASE_URL}/api/v1/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) >= 3:
                    self.test_product_ids = [p['id'] for p in products[:3]]
                    self.log(f"✅ Got {len(self.test_product_ids)} test products: {self.test_product_ids}", GREEN)
                    return True
                else:
                    self.log(f"❌ Not enough products available", RED)
                    return False
            else:
                self.log(f"❌ Failed to fetch products: {response.status_code}", RED)
                return False
        except Exception as e:
            self.log(f"❌ Error fetching products: {e}", RED)
            return False
            
    def get_wishlist(self):
        """Get current wishlist"""
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/wishlist",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('wishlist_items', [])
                return items
            else:
                self.log(f"⚠️ Failed to get wishlist: {response.status_code}", YELLOW)
                return None
        except Exception as e:
            self.log(f"❌ Error getting wishlist: {e}", RED)
            return None
            
    def add_to_wishlist(self, product_id):
        """Add product to wishlist"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/wishlist",
                json={"product_id": product_id},
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get('success', False)
            else:
                self.log(f"⚠️ Failed to add to wishlist: {response.status_code} - {response.text}", YELLOW)
                return False
        except Exception as e:
            self.log(f"❌ Error adding to wishlist: {e}", RED)
            return False
            
    def remove_from_wishlist(self, product_id):
        """Remove product from wishlist"""
        try:
            response = requests.delete(
                f"{BASE_URL}/api/v1/wishlist?product_id={product_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            else:
                self.log(f"⚠️ Failed to remove from wishlist: {response.status_code}", YELLOW)
                return False
        except Exception as e:
            self.log(f"❌ Error removing from wishlist: {e}", RED)
            return False
            
    def run_tests(self):
        """Run all wishlist persistence tests"""
        self.log("=" * 60, BLUE)
        self.log("🧪 WISHLIST PERSISTENCE TEST SUITE", BLUE)
        self.log("=" * 60, BLUE)
        
        # Test 1: Login
        self.log("\n📋 Test 1: Login", YELLOW)
        if not self.login():
            self.test_result("Login", False, "Failed to login")
            return
        self.test_result("Login", True)
        
        # Test 2: Get Products
        self.log("\n📋 Test 2: Get Test Products", YELLOW)
        if not self.get_products():
            self.test_result("Get Products", False, "Failed to get products")
            return
        self.test_result("Get Products", True)
        
        # Test 3: Clear existing wishlist
        self.log("\n📋 Test 3: Clear Existing Wishlist", YELLOW)
        existing = self.get_wishlist()
        if existing is not None:
            for item in existing:
                self.remove_from_wishlist(item['product_id'])
            self.test_result("Clear Wishlist", True, f"Cleared {len(existing)} items")
        else:
            self.test_result("Clear Wishlist", False, "Could not get wishlist")
            
        # Test 4: Add products to wishlist
        self.log("\n📋 Test 4: Add Products to Wishlist", YELLOW)
        added_count = 0
        for product_id in self.test_product_ids:
            if self.add_to_wishlist(product_id):
                added_count += 1
                self.log(f"  ✅ Added product {product_id}", GREEN)
            else:
                self.log(f"  ❌ Failed to add product {product_id}", RED)
        
        self.test_result(
            "Add Products", 
            added_count == len(self.test_product_ids),
            f"Added {added_count}/{len(self.test_product_ids)} products"
        )
        
        # Test 5: Verify wishlist contains added products
        self.log("\n📋 Test 5: Verify Wishlist Contents", YELLOW)
        wishlist = self.get_wishlist()
        if wishlist is not None:
            wishlist_ids = [item['product_id'] for item in wishlist]
            all_present = all(pid in wishlist_ids for pid in self.test_product_ids)
            self.test_result(
                "Verify Contents",
                all_present,
                f"Found {len(wishlist)} items, expected {len(self.test_product_ids)}"
            )
        else:
            self.test_result("Verify Contents", False, "Could not get wishlist")
            
        # Test 6: Logout
        self.log("\n📋 Test 6: Logout", YELLOW)
        self.logout()
        self.test_result("Logout", True, "Token cleared")
        
        # Test 7: Login again
        self.log("\n📋 Test 7: Login Again (New Session)", YELLOW)
        if not self.login():
            self.test_result("Re-login", False, "Failed to login again")
            return
        self.test_result("Re-login", True)
        
        # Test 8: Verify wishlist persists after logout/login
        self.log("\n📋 Test 8: Verify Wishlist Persistence", YELLOW)
        wishlist_after = self.get_wishlist()
        if wishlist_after is not None:
            wishlist_ids_after = [item['product_id'] for item in wishlist_after]
            all_persisted = all(pid in wishlist_ids_after for pid in self.test_product_ids)
            self.test_result(
                "Persistence Check",
                all_persisted,
                f"Found {len(wishlist_after)} items after re-login"
            )
            
            if all_persisted:
                self.log("  ✅ All wishlist items persisted!", GREEN)
            else:
                self.log("  ❌ Some items missing after re-login", RED)
                self.log(f"  Expected: {self.test_product_ids}", YELLOW)
                self.log(f"  Found: {wishlist_ids_after}", YELLOW)
        else:
            self.test_result("Persistence Check", False, "Could not get wishlist")
            
        # Test 9: Remove one item
        self.log("\n📋 Test 9: Remove Item from Wishlist", YELLOW)
        product_to_remove = self.test_product_ids[0]
        if self.remove_from_wishlist(product_to_remove):
            self.log(f"  ✅ Removed product {product_to_remove}", GREEN)
            self.test_result("Remove Item", True)
        else:
            self.log(f"  ❌ Failed to remove product {product_to_remove}", RED)
            self.test_result("Remove Item", False)
            
        # Test 10: Verify removal
        self.log("\n📋 Test 10: Verify Item Removed", YELLOW)
        wishlist_after_removal = self.get_wishlist()
        if wishlist_after_removal is not None:
            wishlist_ids_after_removal = [item['product_id'] for item in wishlist_after_removal]
            removed_correctly = product_to_remove not in wishlist_ids_after_removal
            expected_count = len(self.test_product_ids) - 1
            correct_count = len(wishlist_after_removal) == expected_count
            
            self.test_result(
                "Verify Removal",
                removed_correctly and correct_count,
                f"Wishlist has {len(wishlist_after_removal)} items (expected {expected_count})"
            )
        else:
            self.test_result("Verify Removal", False, "Could not get wishlist")
            
        # Test 11: Logout and login again
        self.log("\n📋 Test 11: Logout and Login Again", YELLOW)
        self.logout()
        if not self.login():
            self.test_result("Final Re-login", False)
            return
        self.test_result("Final Re-login", True)
        
        # Test 12: Verify removal persists
        self.log("\n📋 Test 12: Verify Removal Persists", YELLOW)
        final_wishlist = self.get_wishlist()
        if final_wishlist is not None:
            final_ids = [item['product_id'] for item in final_wishlist]
            removal_persisted = product_to_remove not in final_ids
            expected_count = len(self.test_product_ids) - 1
            correct_count = len(final_wishlist) == expected_count
            
            self.test_result(
                "Removal Persistence",
                removal_persisted and correct_count,
                f"Final wishlist has {len(final_wishlist)} items"
            )
        else:
            self.test_result("Removal Persistence", False, "Could not get wishlist")
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        self.log("\n" + "=" * 60, BLUE)
        self.log("📊 TEST RESULTS SUMMARY", BLUE)
        self.log("=" * 60, BLUE)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = f"{GREEN}✅ PASS{RESET}" if result['passed'] else f"{RED}❌ FAIL{RESET}"
            message = f" - {result['message']}" if result['message'] else ""
            self.log(f"{result['test']}: {status}{message}")
            
        self.log("\n" + "-" * 60, BLUE)
        percentage = (passed / total * 100) if total > 0 else 0
        color = GREEN if percentage == 100 else (YELLOW if percentage >= 70 else RED)
        self.log(f"Total: {passed}/{total} tests passed ({percentage:.1f}%)", color)
        self.log("=" * 60, BLUE)
        
        if percentage == 100:
            self.log("\n🎉 ALL TESTS PASSED! Wishlist persistence is working correctly!", GREEN)
        elif percentage >= 70:
            self.log("\n⚠️ SOME TESTS FAILED. Review the results above.", YELLOW)
        else:
            self.log("\n❌ MANY TESTS FAILED. Wishlist persistence needs attention.", RED)

if __name__ == "__main__":
    print(f"\n{BLUE}{'=' * 60}")
    print("🧪 Wishlist API Persistence Test")
    print(f"{'=' * 60}{RESET}\n")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Account: {TEST_EMAIL}")
    print(f"\n{YELLOW}⚠️ Make sure the backend server is running!{RESET}\n")
    
    input("Press Enter to start tests...")
    
    tester = WishlistTester()
    tester.run_tests()
    
    print(f"\n{BLUE}Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
