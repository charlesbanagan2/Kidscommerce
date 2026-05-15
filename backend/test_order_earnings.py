"""
Test Order Earnings System
Checks all API connections and backend logic for order earnings
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_rider_earnings_endpoint():
    """Test rider earnings API endpoint"""
    print_section("Testing Rider Earnings Endpoint")
    
    # First, login as a rider
    login_data = {
        "email": "rider@test.com",
        "password": "password123"
    }
    
    try:
        # Login
        print("\n1. Logging in as rider...")
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            print(f"   ✓ Login successful")
            print(f"   Token: {access_token[:20]}...")
            
            # Test earnings endpoint
            print("\n2. Fetching rider earnings...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            earnings_response = requests.get(
                f"{BASE_URL}/api/v1/rider/earnings",
                headers=headers
            )
            
            print(f"   Status: {earnings_response.status_code}")
            
            if earnings_response.status_code == 200:
                earnings_data = earnings_response.json()
                print(f"   ✓ Earnings endpoint working!")
                print(f"\n   Earnings Data:")
                print(f"   - Total:      ₱{earnings_data.get('total', 0):.2f}")
                print(f"   - Today:      ₱{earnings_data.get('today', 0):.2f}")
                print(f"   - This Week:  ₱{earnings_data.get('week', 0):.2f}")
                print(f"   - This Month: ₱{earnings_data.get('month', 0):.2f}")
                return True
            else:
                print(f"   ✗ Earnings endpoint failed")
                print(f"   Response: {earnings_response.text}")
                return False
        else:
            print(f"   ✗ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_wallet_transactions():
    """Check wallet transactions table"""
    print_section("Checking Wallet Transactions")
    
    try:
        from app import db, WalletTransaction
        
        print("\n1. Querying wallet transactions...")
        transactions = WalletTransaction.query.order_by(
            WalletTransaction.created_at.desc()
        ).limit(10).all()
        
        if transactions:
            print(f"   ✓ Found {len(transactions)} recent transactions")
            print("\n   Recent Transactions:")
            for tx in transactions:
                print(f"   - User {tx.user_id}: ₱{tx.amount:.2f} ({tx.type}) - {tx.source}")
        else:
            print("   ⚠ No wallet transactions found")
            
        # Check for rider earnings specifically
        print("\n2. Checking rider earnings transactions...")
        rider_earnings = WalletTransaction.query.filter(
            WalletTransaction.source.in_(['order_delivery', 'order_commission'])
        ).all()
        
        if rider_earnings:
            print(f"   ✓ Found {len(rider_earnings)} rider earning transactions")
            total = sum(tx.amount for tx in rider_earnings)
            print(f"   Total rider earnings: ₱{total:.2f}")
        else:
            print("   ⚠ No rider earnings transactions found")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_order_earnings_calculation():
    """Test order earnings calculation logic"""
    print_section("Testing Order Earnings Calculation")
    
    try:
        from app import db, Order, RIDER_EARNING_RATE, SELLER_EARNING_RATE, ADMIN_EARNING_RATE
        
        print("\n1. Checking earnings rates...")
        print(f"   - Rider Rate:  {RIDER_EARNING_RATE * 100}%")
        print(f"   - Seller Rate: {SELLER_EARNING_RATE * 100}%")
        print(f"   - Admin Rate:  {ADMIN_EARNING_RATE * 100}%")
        
        print("\n2. Checking completed orders...")
        completed_orders = Order.query.filter_by(status='completed').all()
        
        if completed_orders:
            print(f"   ✓ Found {len(completed_orders)} completed orders")
            
            # Check a sample order
            sample_order = completed_orders[0]
            print(f"\n   Sample Order #{sample_order.id}:")
            print(f"   - Total Amount: ₱{sample_order.total_amount:.2f}")
            print(f"   - Rider ID: {sample_order.picked_up_by}")
            print(f"   - Status: {sample_order.status}")
            
            if sample_order.picked_up_by:
                expected_rider_earnings = float(sample_order.total_amount) * RIDER_EARNING_RATE
                print(f"   - Expected Rider Earnings: ₱{expected_rider_earnings:.2f}")
        else:
            print("   ⚠ No completed orders found")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_order_status_flow():
    """Test order status flow and earnings triggers"""
    print_section("Testing Order Status Flow")
    
    try:
        from app import db, Order
        
        print("\n1. Checking order statuses...")
        statuses = db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
        
        print("   Order Status Distribution:")
        for status, count in statuses:
            print(f"   - {status}: {count} orders")
            
        print("\n2. Checking orders with riders assigned...")
        orders_with_riders = Order.query.filter(Order.picked_up_by.isnot(None)).all()
        
        if orders_with_riders:
            print(f"   ✓ Found {len(orders_with_riders)} orders with riders")
            
            # Check how many are completed
            completed_with_riders = [o for o in orders_with_riders if o.status == 'completed']
            print(f"   - Completed: {len(completed_with_riders)}")
            print(f"   - In Progress: {len(orders_with_riders) - len(completed_with_riders)}")
        else:
            print("   ⚠ No orders with riders assigned")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False

def test_api_connections():
    """Test all order-related API endpoints"""
    print_section("Testing Order API Connections")
    
    endpoints = [
        ("/api/v1/rider/earnings", "GET", True),
        ("/api/v1/rider/available-orders", "GET", True),
        ("/api/v1/rider/my-deliveries", "GET", True),
        ("/api/v1/buyer/orders", "GET", True),
        ("/api/health", "GET", False),
    ]
    
    results = []
    
    for endpoint, method, requires_auth in endpoints:
        try:
            print(f"\n{endpoint} ({method})...")
            
            if requires_auth:
                print("   (Requires authentication - skipping direct test)")
                results.append((endpoint, "SKIP", "Requires auth"))
            else:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}")
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}")
                    
                if response.status_code in [200, 401, 403]:
                    print(f"   ✓ Endpoint exists (Status: {response.status_code})")
                    results.append((endpoint, "OK", response.status_code))
                else:
                    print(f"   ✗ Unexpected status: {response.status_code}")
                    results.append((endpoint, "FAIL", response.status_code))
                    
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            results.append((endpoint, "ERROR", str(e)))
    
    return results

def main():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  ORDER EARNINGS SYSTEM TEST".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {
        "Rider Earnings Endpoint": False,
        "Wallet Transactions": False,
        "Earnings Calculation": False,
        "Order Status Flow": False,
        "API Connections": False
    }
    
    # Run tests
    results["Rider Earnings Endpoint"] = test_rider_earnings_endpoint()
    results["Wallet Transactions"] = test_wallet_transactions()
    results["Earnings Calculation"] = test_order_earnings_calculation()
    results["Order Status Flow"] = test_order_status_flow()
    
    # Summary
    print_section("TEST SUMMARY")
    print()
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"   {status}  {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("   🎉 ALL TESTS PASSED!")
    else:
        print("   ⚠ SOME TESTS FAILED - Check details above")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
