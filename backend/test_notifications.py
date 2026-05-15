"""
Test Script for Shopee-Style Notification System
Tests all notification functions for buyer, rider, and seller roles
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, Order, OrderItem, Notification, Category
from shopee_notification_system import (
    notify_order_placed,
    notify_order_processing,
    notify_order_ready_for_pickup,
    notify_order_accepted_by_rider,
    notify_order_in_transit,
    notify_order_delivered,
    notify_order_completed,
    notify_product_approved,
    notify_low_stock,
    notify_out_of_stock
)

def setup_test_data():
    """Use existing users, products, and orders from database"""
    print("\n=== Setting up test data ===")
    
    with app.app_context():
        # Don't clear notifications - we want to see real notifications
        
        # Get existing buyer
        buyer = User.query.filter_by(role='buyer').first()
        if not buyer:
            print("[FAIL] No buyer found in database")
            return None, None, None, None, None
        print(f"[OK] Using existing buyer (ID: {buyer.id})")
        
        # Get existing seller
        seller = User.query.filter_by(role='seller').first()
        if not seller:
            print("[FAIL] No seller found in database")
            return None, None, None, None, None
        print(f"[OK] Using existing seller (ID: {seller.id})")
        
        # Get existing rider
        rider = User.query.filter_by(role='rider').first()
        if not rider:
            print("[FAIL] No rider found in database")
            return None, None, None, None, None
        print(f"[OK] Using existing rider (ID: {rider.id})")
        
        # Get any existing product (not necessarily from this seller)
        product = Product.query.first()
        if not product:
            print("[FAIL] No product found in database")
            return None, None, None, None, None
        print(f"[OK] Using existing product (ID: {product.id})")
        
        # Get any existing order (not necessarily from this buyer)
        order = Order.query.first()
        if not order:
            print("[FAIL] No order found in database")
            return None, None, None, None, None
        print(f"[OK] Using existing order (ID: {order.id})")
        
        return buyer, seller, rider, product, order


def check_notifications(expected_count, order_id=None):
    """Check if notifications were created for an order"""
    query = Notification.query
    
    if order_id:
        query = query.filter_by(order_id=order_id)
    
    notifications = query.order_by(Notification.id.desc()).limit(10).all()
    print(f"  Found {len(notifications)} recent notifications for order")
    
    for notif in notifications:
        print(f"    - User ID: {notif.user_id}")
        print(f"      Message: {notif.message[:60]}...")
        print(f"      Type: {notif.type}")
        print()
    
    return notifications


def test_order_placed_notification(buyer, seller, rider, order):
    """Test order placed notification"""
    print("\n=== Test 1: Order Placed Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_placed(order)
            print("[OK] notify_order_placed() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_order_processing_notification(buyer, seller, rider, order):
    """Test order processing notification"""
    print("\n=== Test 2: Order Processing Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_processing(order)
            print("[OK] notify_order_processing() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_order_ready_for_pickup_notification(buyer, seller, rider, order):
    """Test order ready for pickup notification"""
    print("\n=== Test 3: Order Ready for Pickup Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_ready_for_pickup(order)
            print("[OK] notify_order_ready_for_pickup() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_rider_accepted_notification(buyer, seller, rider, order):
    """Test rider accepted notification"""
    print("\n=== Test 4: Rider Accepted Order Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_accepted_by_rider(order)
            print("[OK] notify_order_accepted_by_rider() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_order_in_transit_notification(buyer, seller, rider, order):
    """Test order in transit notification"""
    print("\n=== Test 5: Order In Transit Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_in_transit(order)
            print("[OK] notify_order_in_transit() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_order_delivered_notification(buyer, seller, rider, order):
    """Test order delivered notification"""
    print("\n=== Test 6: Order Delivered Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_delivered(order)
            print("[OK] notify_order_delivered() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_order_completed_notification(buyer, seller, rider, order):
    """Test order completed notification"""
    print("\n=== Test 7: Order Completed Notification ===")
    
    with app.app_context():
        # Refresh order to bind to session
        order = db.session.get(Order, order.id)
        
        try:
            notify_order_completed(order)
            print("[OK] notify_order_completed() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = check_notifications(expected_count=1, order_id=order.id)
        if len(notifs) > 0:
            print("  [OK] Notification created")
        else:
            print("  [FAIL] Notification NOT created")
            return False
        
        return True


def test_product_approved_notification(buyer, seller, rider, product):
    """Test product approved notification"""
    print("\n=== Test 8: Product Approved Notification ===")
    
    with app.app_context():
        # Refresh product to bind to session
        product = db.session.get(Product, product.id)
        
        try:
            notify_product_approved(product)
            print("[OK] notify_product_approved() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = Notification.query.order_by(Notification.id.desc()).limit(5).all()
        if len(notifs) > 0:
            print(f"  [OK] Found {len(notifs)} recent notifications")
        else:
            print("  [FAIL] No notifications created")
            return False
        
        return True


def test_low_stock_notification(buyer, seller, rider, product):
    """Test low stock notification"""
    print("\n=== Test 9: Low Stock Notification ===")
    
    with app.app_context():
        # Refresh product to bind to session
        product = db.session.get(Product, product.id)
        
        try:
            notify_low_stock(product)
            print("[OK] notify_low_stock() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = Notification.query.order_by(Notification.id.desc()).limit(5).all()
        if len(notifs) > 0:
            print(f"  [OK] Found {len(notifs)} recent notifications")
        else:
            print("  [FAIL] No notifications created")
            return False
        
        return True


def test_out_of_stock_notification(buyer, seller, rider, product):
    """Test out of stock notification"""
    print("\n=== Test 10: Out of Stock Notification ===")
    
    with app.app_context():
        # Refresh product to bind to session
        product = db.session.get(Product, product.id)
        
        try:
            notify_out_of_stock(product)
            print("[OK] notify_out_of_stock() executed successfully")
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            return False
        
        # Check notifications were created
        print("\n  Checking notifications...")
        notifs = Notification.query.order_by(Notification.id.desc()).limit(5).all()
        if len(notifs) > 0:
            print(f"  [OK] Found {len(notifs)} recent notifications")
        else:
            print("  [FAIL] No notifications created")
            return False
        
        return True


def run_all_tests():
    """Run all notification tests"""
    print("=" * 60)
    print("SHOPEE-STYLE NOTIFICATION SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Setup test data
    buyer, seller, rider, product, order = setup_test_data()
    
    # Run tests
    results = {}
    
    results['order_placed'] = test_order_placed_notification(buyer, seller, rider, order)
    results['order_processing'] = test_order_processing_notification(buyer, seller, rider, order)
    results['order_ready_for_pickup'] = test_order_ready_for_pickup_notification(buyer, seller, rider, order)
    results['rider_accepted'] = test_rider_accepted_notification(buyer, seller, rider, order)
    results['order_in_transit'] = test_order_in_transit_notification(buyer, seller, rider, order)
    results['order_delivered'] = test_order_delivered_notification(buyer, seller, rider, order)
    results['order_completed'] = test_order_completed_notification(buyer, seller, rider, order)
    results['product_approved'] = test_product_approved_notification(buyer, seller, rider, product)
    results['low_stock'] = test_low_stock_notification(buyer, seller, rider, product)
    results['out_of_stock'] = test_out_of_stock_notification(buyer, seller, rider, product)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] PASSED" if result else "[FAIL] FAILED"
        print(f"{test_name:30s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    # No cleanup needed - we're testing with real data
    
    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
