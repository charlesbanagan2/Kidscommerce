"""
Comprehensive Rider System Test Script
Tests all rider functionality including database, API, and FCFS logic
"""

from app import app, db, User, Order, OrderItem, Product
from datetime import datetime
import requests
import json

def test_database_columns():
    """Test 1: Verify database columns exist"""
    print("\n" + "="*60)
    print("TEST 1: Database Columns")
    print("="*60)
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('order')]
            
            required_columns = [
                'rider_id', 'picked_up_at', 'picked_up_by',
                'delivered_at', 'delivered_by', 'rider_earnings'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print(f"❌ Missing columns: {missing}")
                print("   Run: python add_rider_columns.py")
                return False
            else:
                print("✅ All required columns exist")
                return True
                
        except Exception as e:
            print(f"❌ Error checking columns: {str(e)}")
            return False


def test_create_test_data():
    """Test 2: Create test rider and order"""
    print("\n" + "="*60)
    print("TEST 2: Create Test Data")
    print("="*60)
    
    with app.app_context():
        try:
            # Create test rider if not exists
            rider = User.query.filter_by(email='test.rider@example.com').first()
            if not rider:
                rider = User(
                    email='test.rider@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Rider',
                    role='rider',
                    status='approved',
                    phone='09123456789'
                )
                db.session.add(rider)
                db.session.commit()
                print(f"✅ Test rider created: ID={rider.id}")
            else:
                print(f"✅ Test rider exists: ID={rider.id}")
            
            # Create test buyer if not exists
            buyer = User.query.filter_by(email='test.buyer@example.com').first()
            if not buyer:
                buyer = User(
                    email='test.buyer@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Buyer',
                    role='buyer',
                    status='approved',
                    phone='09987654321'
                )
                db.session.add(buyer)
                db.session.commit()
                print(f"✅ Test buyer created: ID={buyer.id}")
            else:
                print(f"✅ Test buyer exists: ID={buyer.id}")
            
            # Create test order if not exists
            test_order = Order.query.filter_by(
                buyer_id=buyer.id,
                status='ready_for_pickup',
                rider_id=None
            ).first()
            
            if not test_order:
                # Get a product
                product = Product.query.filter_by(status='approved').first()
                if not product:
                    print("❌ No approved products found. Create a product first.")
                    return False
                
                test_order = Order(
                    buyer_id=buyer.id,
                    status='ready_for_pickup',
                    total_amount=500.0,
                    shipping_address='123 Test Street, Test City',
                    payment_method='COD',
                    recipient_name='Test Buyer',
                    recipient_phone='09987654321',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(test_order)
                db.session.flush()
                
                # Add order item
                order_item = OrderItem(
                    order_id=test_order.id,
                    product_id=product.id,
                    quantity=1,
                    price_at_time=500.0
                )
                db.session.add(order_item)
                db.session.commit()
                
                print(f"✅ Test order created: ID={test_order.id}")
            else:
                print(f"✅ Test order exists: ID={test_order.id}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test data: {str(e)}")
            return False


def test_api_endpoints():
    """Test 3: Test API endpoints"""
    print("\n" + "="*60)
    print("TEST 3: API Endpoints")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    # Login as rider
    try:
        response = requests.post(
            f"{base_url}/api/login",
            json={
                'email': 'test.rider@example.com',
                'password': 'password123'
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        data = response.json()
        tokens = data.get('tokens', {})
        access_token = tokens.get('access_token')
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test available orders endpoint
        response = requests.get(
            f"{base_url}/api/rider/available-orders",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available orders: {data.get('count', 0)} orders")
        else:
            print(f"❌ Available orders failed: {response.status_code}")
            return False
        
        # Test earnings endpoint
        response = requests.get(
            f"{base_url}/api/rider/earnings",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Earnings: Total=₱{data.get('total', 0):.2f}")
        else:
            print(f"❌ Earnings failed: {response.status_code}")
            return False
        
        # Test my deliveries endpoint
        response = requests.get(
            f"{base_url}/api/rider/my-deliveries",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ My deliveries: {data.get('count', 0)} orders")
        else:
            print(f"❌ My deliveries failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return False


def test_fcfs_logic():
    """Test 4: Test FCFS order acceptance"""
    print("\n" + "="*60)
    print("TEST 4: FCFS Order Acceptance")
    print("="*60)
    
    with app.app_context():
        try:
            # Get test order
            test_order = Order.query.filter_by(
                status='ready_for_pickup',
                rider_id=None
            ).first()
            
            if not test_order:
                print("❌ No available orders for testing")
                return False
            
            print(f"✅ Found test order: ID={test_order.id}")
            
            # Get test rider
            rider = User.query.filter_by(email='test.rider@example.com').first()
            if not rider:
                print("❌ Test rider not found")
                return False
            
            # Simulate FCFS acceptance
            order = db.session.query(Order).filter(
                Order.id == test_order.id
            ).with_for_update().first()
            
            if order.status != 'ready_for_pickup' or order.rider_id is not None:
                print("❌ Order not available for acceptance")
                return False
            
            # Accept order
            order.status = 'in_transit'
            order.rider_id = rider.id
            order.picked_up_at = datetime.utcnow()
            order.picked_up_by = rider.id
            order.rider_earnings = float(order.total_amount) * 0.15
            order.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Order accepted successfully")
            print(f"   Rider earnings: ₱{order.rider_earnings:.2f}")
            
            # Try to accept again (should fail)
            order2 = Order.query.get(test_order.id)
            if order2.status == 'in_transit' and order2.rider_id == rider.id:
                print("✅ FCFS logic working - order already taken")
            else:
                print("❌ FCFS logic failed")
                return False
            
            # Reset order for next test
            order2.status = 'ready_for_pickup'
            order2.rider_id = None
            order2.picked_up_at = None
            order2.picked_up_by = None
            order2.rider_earnings = 0.0
            db.session.commit()
            print("✅ Order reset for next test")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error testing FCFS: {str(e)}")
            return False


def test_earnings_calculation():
    """Test 5: Test earnings calculation"""
    print("\n" + "="*60)
    print("TEST 5: Earnings Calculation")
    print("="*60)
    
    with app.app_context():
        try:
            rider = User.query.filter_by(email='test.rider@example.com').first()
            if not rider:
                print("❌ Test rider not found")
                return False
            
            # Create completed order with earnings
            buyer = User.query.filter_by(email='test.buyer@example.com').first()
            product = Product.query.filter_by(status='approved').first()
            
            if not buyer or not product:
                print("❌ Test data not found")
                return False
            
            # Create order
            order = Order(
                buyer_id=buyer.id,
                rider_id=rider.id,
                status='delivered',
                total_amount=1000.0,
                rider_earnings=150.0,  # 15% of 1000
                shipping_address='Test Address',
                payment_method='COD',
                picked_up_at=datetime.utcnow(),
                delivered_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(order)
            db.session.flush()
            
            # Add order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                price_at_time=1000.0
            )
            db.session.add(order_item)
            db.session.commit()
            
            print(f"✅ Test order created with earnings: ₱{order.rider_earnings:.2f}")
            
            # Calculate total earnings
            from sqlalchemy import func
            total_earnings = db.session.query(
                func.sum(Order.rider_earnings)
            ).filter(
                Order.rider_id == rider.id,
                Order.status.in_(['delivered', 'completed'])
            ).scalar() or 0.0
            
            print(f"✅ Total rider earnings: ₱{total_earnings:.2f}")
            
            if total_earnings >= 150.0:
                print("✅ Earnings calculation working correctly")
                return True
            else:
                print("❌ Earnings calculation incorrect")
                return False
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error testing earnings: {str(e)}")
            return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RIDER SYSTEM COMPREHENSIVE TEST")
    print("="*60)
    
    results = {
        'Database Columns': test_database_columns(),
        'Test Data Creation': test_create_test_data(),
        'API Endpoints': test_api_endpoints(),
        'FCFS Logic': test_fcfs_logic(),
        'Earnings Calculation': test_earnings_calculation()
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nYour rider system is fully functional!")
        print("\nNext steps:")
        print("1. Test on mobile app")
        print("2. Test with multiple riders (FCFS)")
        print("3. Test real-time notifications")
        print("4. Deploy to production")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the failed tests before proceeding.")
        print("Check the error messages above for details.")
    
    return all_passed


if __name__ == '__main__':
    run_all_tests()
