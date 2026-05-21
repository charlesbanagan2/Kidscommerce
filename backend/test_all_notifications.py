"""
Comprehensive Notification System Test Script
Tests all notification triggers for Buyer, Seller, Rider, and Admin
"""
import sys
from app import app, db, User, Order, Product, Notification
from shopee_notification_system import *

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def get_test_users():
    """Get or create test users for each role"""
    with app.app_context():
        buyer = User.query.filter_by(role='buyer', status='active').first()
        seller = User.query.filter_by(role='seller', status='active').first()
        rider = User.query.filter_by(role='rider', status='active').first()
        admin = User.query.filter_by(role='admin').first()
        
        if not buyer:
            print_error("No active buyer found in database")
            return None, None, None, None
        if not seller:
            print_error("No active seller found in database")
            return None, None, None, None
        if not rider:
            print_error("No active rider found in database")
            return None, None, None, None
        if not admin:
            print_error("No admin found in database")
            return None, None, None, None
            
        print_success(f"Buyer: {buyer.first_name} {buyer.last_name} (ID: {buyer.id})")
        print_success(f"Seller: {seller.first_name} {seller.last_name} (ID: {seller.id})")
        print_success(f"Rider: {rider.first_name} {rider.last_name} (ID: {rider.id})")
        print_success(f"Admin: {admin.first_name} {admin.last_name} (ID: {admin.id})")
        
        return buyer, seller, rider, admin

def test_order_notifications():
    """Test all order-related notifications"""
    print_header("Testing Order Notifications")
    
    with app.app_context():
        # Get test order
        order = Order.query.filter_by(status='pending').first()
        if not order:
            order = Order.query.first()
        
        if not order:
            print_error("No orders found in database")
            return
        
        print_info(f"Using Order ID: {order.id}")
        
        # Test 1: Order Placed
        try:
            notify_order_placed(order)
            print_success("Order Placed notification sent")
        except Exception as e:
            print_error(f"Order Placed notification failed: {e}")
        
        # Test 2: Order Confirmed
        try:
            notify_order_confirmed(order)
            print_success("Order Confirmed notification sent")
        except Exception as e:
            print_error(f"Order Confirmed notification failed: {e}")
        
        # Test 3: Order Processing
        try:
            notify_order_processing(order)
            print_success("Order Processing notification sent")
        except Exception as e:
            print_error(f"Order Processing notification failed: {e}")
        
        # Test 4: Ready for Pickup
        try:
            notify_order_ready_for_pickup(order)
            print_success("Ready for Pickup notification sent (broadcast to all riders)")
        except Exception as e:
            print_error(f"Ready for Pickup notification failed: {e}")
        
        # Test 5: Rider Accepts Order
        if order.rider_id:
            try:
                notify_order_accepted_by_rider(order)
                print_success("Rider Accepted notification sent")
            except Exception as e:
                print_error(f"Rider Accepted notification failed: {e}")
        else:
            print_info("Skipping Rider Accepted (no rider assigned)")
        
        # Test 6: Order In Transit
        try:
            notify_order_in_transit(order)
            print_success("Order In Transit notification sent")
        except Exception as e:
            print_error(f"Order In Transit notification failed: {e}")
        
        # Test 7: Order Delivered
        try:
            notify_order_delivered(order)
            print_success("Order Delivered notification sent")
        except Exception as e:
            print_error(f"Order Delivered notification failed: {e}")
        
        # Test 8: Order Completed
        try:
            notify_order_completed(order)
            print_success("Order Completed notification sent")
        except Exception as e:
            print_error(f"Order Completed notification failed: {e}")
        
        # Test 9: Order Cancelled
        try:
            notify_order_cancelled(order, cancelled_by='admin')
            print_success("Order Cancelled notification sent")
        except Exception as e:
            print_error(f"Order Cancelled notification failed: {e}")

def test_payment_notifications():
    """Test payment-related notifications"""
    print_header("Testing Payment Notifications")
    
    with app.app_context():
        order = Order.query.first()
        if not order:
            print_error("No orders found in database")
            return
        
        print_info(f"Using Order ID: {order.id}")
        
        # Test 1: Payment Confirmed
        try:
            notify_payment_confirmed(order)
            print_success("Payment Confirmed notification sent")
        except Exception as e:
            print_error(f"Payment Confirmed notification failed: {e}")
        
        # Test 2: Refund Processed
        try:
            notify_refund_processed(order, 500.00)
            print_success("Refund Processed notification sent")
        except Exception as e:
            print_error(f"Refund Processed notification failed: {e}")

def test_return_notifications():
    """Test return/refund notifications"""
    print_header("Testing Return & Refund Notifications")
    
    with app.app_context():
        order = Order.query.first()
        if not order:
            print_error("No orders found in database")
            return
        
        print_info(f"Using Order ID: {order.id}")
        
        # Test 1: Return Requested
        try:
            notify_return_requested(order, reason='Product defective')
            print_success("Return Requested notification sent")
        except Exception as e:
            print_error(f"Return Requested notification failed: {e}")
        
        # Test 2: Return Approved
        try:
            notify_return_approved(order)
            print_success("Return Approved notification sent")
        except Exception as e:
            print_error(f"Return Approved notification failed: {e}")
        
        # Test 3: Return Rejected
        try:
            notify_return_rejected(order, reason='Return period expired')
            print_success("Return Rejected notification sent")
        except Exception as e:
            print_error(f"Return Rejected notification failed: {e}")

def test_product_notifications():
    """Test product-related notifications"""
    print_header("Testing Product Notifications")
    
    with app.app_context():
        product = Product.query.first()
        if not product:
            print_error("No products found in database")
            return
        
        print_info(f"Using Product: {product.name} (ID: {product.id})")
        
        # Test 1: Product Approved
        try:
            notify_product_approved(product)
            print_success("Product Approved notification sent")
        except Exception as e:
            print_error(f"Product Approved notification failed: {e}")
        
        # Test 2: Product Rejected
        try:
            notify_product_rejected(product, reason='Incomplete product information')
            print_success("Product Rejected notification sent")
        except Exception as e:
            print_error(f"Product Rejected notification failed: {e}")
        
        # Test 3: Low Stock Alert
        try:
            notify_low_stock(product)
            print_success("Low Stock Alert notification sent")
        except Exception as e:
            print_error(f"Low Stock Alert notification failed: {e}")
        
        # Test 4: Out of Stock
        try:
            notify_out_of_stock(product)
            print_success("Out of Stock notification sent")
        except Exception as e:
            print_error(f"Out of Stock notification failed: {e}")

def test_account_notifications():
    """Test account-related notifications"""
    print_header("Testing Account Notifications")
    
    with app.app_context():
        buyer, seller, rider, admin = get_test_users()
        if not buyer:
            return
        
        # Test 1: Account Approved
        try:
            notify_account_approved(buyer)
            print_success("Account Approved notification sent")
        except Exception as e:
            print_error(f"Account Approved notification failed: {e}")
        
        # Test 2: Account Rejected
        try:
            notify_account_rejected(buyer, reason='Invalid documents')
            print_success("Account Rejected notification sent")
        except Exception as e:
            print_error(f"Account Rejected notification failed: {e}")

def test_system_notifications():
    """Test system notifications"""
    print_header("Testing System Notifications")
    
    with app.app_context():
        buyer, seller, rider, admin = get_test_users()
        if not buyer:
            return
        
        # Test 1: Promotion Available
        try:
            notify_promotion_available(
                buyer, 
                "Flash Sale - 50% Off!", 
                "Get 50% off on all baby products today only!"
            )
            print_success("Promotion notification sent")
        except Exception as e:
            print_error(f"Promotion notification failed: {e}")
        
        # Test 2: System Maintenance
        try:
            notify_system_maintenance(
                buyer,
                "System will be down for maintenance on Sunday, 2AM-4AM"
            )
            print_success("System Maintenance notification sent")
        except Exception as e:
            print_error(f"System Maintenance notification failed: {e}")

def test_chat_notifications():
    """Test chat notifications"""
    print_header("Testing Chat Notifications")
    
    with app.app_context():
        buyer, seller, rider, admin = get_test_users()
        if not buyer:
            return
        
        # Test: New Message
        try:
            notify_new_message(
                buyer.id,
                f"{seller.first_name} {seller.last_name}",
                "Hello! Is this product still available?"
            )
            print_success("New Message notification sent")
        except Exception as e:
            print_error(f"New Message notification failed: {e}")

def check_notification_counts():
    """Check notification counts in database"""
    print_header("Notification Database Summary")
    
    with app.app_context():
        total = Notification.query.count()
        unread = Notification.query.filter_by(is_read=False).count()
        
        by_type = db.session.query(
            Notification.type, 
            db.func.count(Notification.id)
        ).group_by(Notification.type).all()
        
        by_user = db.session.query(
            User.role,
            db.func.count(Notification.id)
        ).join(User, Notification.user_id == User.id).group_by(User.role).all()
        
        print_info(f"Total Notifications: {total}")
        print_info(f"Unread Notifications: {unread}")
        print_info(f"Read Notifications: {total - unread}")
        
        print("\nNotifications by Type:")
        for notif_type, count in by_type:
            print(f"  - {notif_type or 'None'}: {count}")
        
        print("\nNotifications by User Role:")
        for role, count in by_user:
            print(f"  - {role}: {count}")

def main():
    """Run all notification tests"""
    print_header("🔔 Comprehensive Notification System Test")
    print_info("This script will test all notification triggers")
    print_info("Notifications will be created in the database")
    print("")
    
    # Check test users
    with app.app_context():
        buyer, seller, rider, admin = get_test_users()
        if not buyer:
            print_error("Cannot proceed without test users")
            return
    
    # Run all tests
    test_order_notifications()
    test_payment_notifications()
    test_return_notifications()
    test_product_notifications()
    test_account_notifications()
    test_system_notifications()
    test_chat_notifications()
    
    # Show summary
    check_notification_counts()
    
    print_header("✅ Notification Test Complete")
    print_info("Check the mobile app to see the notifications")
    print_info("Login as buyer, seller, or rider to view notifications")

if __name__ == '__main__':
    main()
