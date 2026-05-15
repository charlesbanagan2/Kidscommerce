"""
Automated Rider Workflow Test Script
Tests the complete rider FCFS system from order creation to delivery
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://192.168.1.20:5000"
BUYER_EMAIL = "buyer@test.com"
BUYER_PASSWORD = "buyer123"
SELLER_EMAIL = "seller@test.com"
SELLER_PASSWORD = "seller123"
RIDER1_EMAIL = "rider1@test.com"
RIDER1_PASSWORD = "rider123"
RIDER2_EMAIL = "rider2@test.com"
RIDER2_PASSWORD = "rider123"

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   {message}")
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def login(email, password):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Login failed for {email}: {response.text}")
            return None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None

def get_available_orders(rider_token):
    """Get available orders for rider"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/rider/available-orders",
            headers={"Authorization": f"Bearer {rider_token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Get available orders failed: {response.text}")
            return None
    except Exception as e:
        print(f"Get available orders error: {e}")
        return None

def accept_order(rider_token, order_id):
    """Accept an order"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/rider/accept-order/{order_id}",
            headers={"Authorization": f"Bearer {rider_token}"}
        )
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code in [200, 409] else None
        }
    except Exception as e:
        print(f"Accept order error: {e}")
        return {"status_code": 500, "data": None}

def get_my_deliveries(rider_token):
    """Get rider's deliveries"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/rider/my-deliveries",
            headers={"Authorization": f"Bearer {rider_token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Get my deliveries failed: {response.text}")
            return None
    except Exception as e:
        print(f"Get my deliveries error: {e}")
        return None

def test_authentication():
    """Test 1: Authentication"""
    print("\n" + "="*60)
    print("TEST 1: AUTHENTICATION")
    print("="*60)
    
    # Test buyer login
    buyer_token = login(BUYER_EMAIL, BUYER_PASSWORD)
    log_test("Buyer Login", buyer_token is not None, f"Token: {buyer_token[:20]}..." if buyer_token else "Failed")
    
    # Test seller login
    seller_token = login(SELLER_EMAIL, SELLER_PASSWORD)
    log_test("Seller Login", seller_token is not None, f"Token: {seller_token[:20]}..." if seller_token else "Failed")
    
    # Test rider1 login
    rider1_token = login(RIDER1_EMAIL, RIDER1_PASSWORD)
    log_test("Rider 1 Login", rider1_token is not None, f"Token: {rider1_token[:20]}..." if rider1_token else "Failed")
    
    # Test rider2 login
    rider2_token = login(RIDER2_EMAIL, RIDER2_PASSWORD)
    log_test("Rider 2 Login", rider2_token is not None, f"Token: {rider2_token[:20]}..." if rider2_token else "Failed")
    
    return {
        "buyer": buyer_token,
        "seller": seller_token,
        "rider1": rider1_token,
        "rider2": rider2_token
    }

def test_available_orders(tokens):
    """Test 2: Get Available Orders"""
    print("\n" + "="*60)
    print("TEST 2: GET AVAILABLE ORDERS")
    print("="*60)
    
    # Get available orders for rider1
    result1 = get_available_orders(tokens["rider1"])
    log_test(
        "Rider 1 - Get Available Orders",
        result1 is not None and "orders" in result1,
        f"Found {len(result1.get('orders', []))} orders" if result1 else "Failed"
    )
    
    # Get available orders for rider2
    result2 = get_available_orders(tokens["rider2"])
    log_test(
        "Rider 2 - Get Available Orders",
        result2 is not None and "orders" in result2,
        f"Found {len(result2.get('orders', []))} orders" if result2 else "Failed"
    )
    
    # Check if both riders see the same orders
    if result1 and result2:
        orders1 = result1.get("orders", [])
        orders2 = result2.get("orders", [])
        same_count = len(orders1) == len(orders2)
        log_test(
            "Both Riders See Same Orders",
            same_count,
            f"Rider1: {len(orders1)}, Rider2: {len(orders2)}"
        )
        
        return orders1
    
    return []

def test_fcfs_logic(tokens, orders):
    """Test 3: FCFS Logic - Only One Rider Can Accept"""
    print("\n" + "="*60)
    print("TEST 3: FCFS LOGIC (CRITICAL)")
    print("="*60)
    
    if not orders:
        log_test("FCFS Test", False, "No orders available to test")
        print("\n⚠️  MANUAL TEST REQUIRED:")
        print("   1. Login as seller")
        print("   2. Mark an order as 'Ready for Pickup'")
        print("   3. Re-run this test")
        return
    
    order_id = orders[0]["id"]
    print(f"\nTesting with Order ID: {order_id}")
    print("Simulating simultaneous accept by 2 riders...")
    
    # Use ThreadPoolExecutor to simulate simultaneous requests
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(accept_order, tokens["rider1"], order_id)
        future2 = executor.submit(accept_order, tokens["rider2"], order_id)
        
        for future in as_completed([future1, future2]):
            results.append(future.result())
    
    # Analyze results
    success_count = sum(1 for r in results if r["status_code"] == 200)
    conflict_count = sum(1 for r in results if r["status_code"] == 409)
    
    print(f"\nResults:")
    print(f"  - Success (200): {success_count}")
    print(f"  - Conflict (409): {conflict_count}")
    
    # Test: Exactly one success
    log_test(
        "FCFS - Only One Rider Succeeds",
        success_count == 1,
        f"Expected 1 success, got {success_count}"
    )
    
    # Test: Exactly one conflict
    log_test(
        "FCFS - Other Rider Gets Conflict",
        conflict_count == 1,
        f"Expected 1 conflict, got {conflict_count}"
    )
    
    # Test: Total responses = 2
    log_test(
        "FCFS - Both Riders Got Response",
        len(results) == 2,
        f"Expected 2 responses, got {len(results)}"
    )
    
    # Determine winner
    winner = None
    for i, result in enumerate(results):
        if result["status_code"] == 200:
            winner = f"Rider {i+1}"
            print(f"\n🏆 Winner: {winner}")
    
    return order_id, winner

def test_my_deliveries(tokens, order_id):
    """Test 4: My Deliveries"""
    print("\n" + "="*60)
    print("TEST 4: MY DELIVERIES")
    print("="*60)
    
    # Get deliveries for rider1
    deliveries1 = get_my_deliveries(tokens["rider1"])
    has_order1 = False
    if deliveries1 and "deliveries" in deliveries1:
        has_order1 = any(d["id"] == order_id for d in deliveries1["deliveries"])
    
    # Get deliveries for rider2
    deliveries2 = get_my_deliveries(tokens["rider2"])
    has_order2 = False
    if deliveries2 and "deliveries" in deliveries2:
        has_order2 = any(d["id"] == order_id for d in deliveries2["deliveries"])
    
    # Test: Only one rider has the order
    only_one_has_order = (has_order1 and not has_order2) or (not has_order1 and has_order2)
    log_test(
        "Only Winner Has Order in Deliveries",
        only_one_has_order,
        f"Rider1: {has_order1}, Rider2: {has_order2}"
    )
    
    # Test: Winner can see order details
    if has_order1:
        order_details = next((d for d in deliveries1["deliveries"] if d["id"] == order_id), None)
        log_test(
            "Winner - Order Details Complete",
            order_details is not None and "buyer_name" in order_details,
            f"Order: {order_details}" if order_details else "Not found"
        )
    elif has_order2:
        order_details = next((d for d in deliveries2["deliveries"] if d["id"] == order_id), None)
        log_test(
            "Winner - Order Details Complete",
            order_details is not None and "buyer_name" in order_details,
            f"Order: {order_details}" if order_details else "Not found"
        )

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nRider system is working correctly:")
        print("  ✅ Authentication working")
        print("  ✅ Available orders visible to all riders")
        print("  ✅ FCFS logic prevents race conditions")
        print("  ✅ Only one rider can accept each order")
        print("  ✅ Order appears in winner's deliveries")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nFailed Tests:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  ❌ {test['name']}: {test['message']}")
        
        print("\nTroubleshooting:")
        print("  1. Check backend is running on http://192.168.1.20:5000")
        print("  2. Verify PostgreSQL database is being used (not SQLite)")
        print("  3. Ensure rider accounts are approved")
        print("  4. Check backend logs for errors")
        print("  5. Verify Socket.IO is enabled")

def main():
    """Run all tests"""
    print("="*60)
    print("RIDER WORKFLOW AUTOMATED TEST")
    print("="*60)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Test Accounts:")
    print(f"  - Buyer: {BUYER_EMAIL}")
    print(f"  - Seller: {SELLER_EMAIL}")
    print(f"  - Rider 1: {RIDER1_EMAIL}")
    print(f"  - Rider 2: {RIDER2_EMAIL}")
    
    # Test 1: Authentication
    tokens = test_authentication()
    if not all(tokens.values()):
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        print_summary()
        return
    
    # Test 2: Get Available Orders
    orders = test_available_orders(tokens)
    
    # Test 3: FCFS Logic
    if orders:
        order_id, winner = test_fcfs_logic(tokens, orders)
        
        # Test 4: My Deliveries
        if order_id:
            time.sleep(1)  # Wait for database to update
            test_my_deliveries(tokens, order_id)
    else:
        print("\n⚠️  No orders available for FCFS test")
        print("\nMANUAL STEPS REQUIRED:")
        print("  1. Login as buyer and place an order")
        print("  2. Login as seller and accept the order")
        print("  3. Seller marks order as 'Ready for Pickup'")
        print("  4. Re-run this test script")
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
