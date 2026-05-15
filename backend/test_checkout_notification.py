"""
Test checkout notification creation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, Order, Notification

def test_checkout_notification():
    """Test that checkout creates a notification"""
    print("=" * 70)
    print("CHECKOUT NOTIFICATION TEST")
    print("=" * 70)
    
    with app.app_context():
        # Get or create test buyer and seller
        buyer = User.query.filter_by(role='buyer').first()
        seller = User.query.filter_by(role='seller').first()
        
        if not buyer:
            print("[!] No buyer found - cannot test")
            return
        
        if not seller:
            print("[!] No seller found - cannot test")
            return
        
        print(f"\n[OK] Buyer: {buyer.id} - {buyer.email}")
        print(f"[OK] Seller: {seller.id} - {seller.email}")
        
        # Get a product for the seller
        product = Product.query.filter_by(seller_id=seller.id, status='active').first()
        if not product:
            print("[!] No active product found - creating test product")
            product = Product(
                name="Test Product",
                price=100.0,
                stock=50,
                seller_id=seller.id,
                status='active'
            )
            db.session.add(product)
            db.session.commit()
            print(f"[OK] Created product: {product.id}")
        
        print(f"[OK] Product: {product.id} - {product.name}")
        
        # Clear existing notifications for buyer
        Notification.query.filter_by(user_id=buyer.id).delete()
        db.session.commit()
        print("\n[OK] Cleared existing notifications")
        
        # Simulate checkout notification creation
        print("\n[1] Creating order notification...")
        try:
            from shopee_notification_system import create_notification
            
            # Create buyer notification
            create_notification(
                user_id=buyer.id,
                title="Order Placed Successfully",
                message=f"Your order #999 has been placed. Waiting for seller confirmation.",
                notification_type='order',
                order_id=999,
                action_url='/buyer/orders/999'
            )
            print("[OK] Buyer notification created")
            
            # Create seller notification
            create_notification(
                user_id=seller.id,
                title="[CART] New Order Received!",
                message=f"Order #999 from Test Buyer. Total: PHP100.00",
                notification_type='order',
                order_id=999,
                action_url='/seller/orders/999'
            )
            print("[OK] Seller notification created")
            
        except Exception as e:
            print(f"[ERROR] Failed to create notification: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Verify notifications were created
        print("\n[2] Verifying notifications...")
        buyer_notifs = Notification.query.filter_by(user_id=buyer.id).all()
        seller_notifs = Notification.query.filter_by(user_id=seller.id).all()
        
        print(f"  Buyer notifications: {len(buyer_notifs)}")
        print(f"  Seller notifications: {len(seller_notifs)}")
        
        if buyer_notifs:
            for notif in buyer_notifs:
                print(f"    - [{notif.type}] {notif.title}")
        
        if seller_notifs:
            for notif in seller_notifs:
                print(f"    - [{notif.type}] {notif.title}")
        
        # Test API endpoint
        print("\n[3] Testing unread count API...")
        try:
            from notification_api_endpoints import get_unread_count
            result, status = get_unread_count(buyer.id, 'buyer')
            print(f"  Status: {status}")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 70)
        if buyer_notifs and seller_notifs:
            print("[OK] TEST PASSED - Notifications created successfully")
        else:
            print("[FAIL] TEST FAILED - Notifications not created")
        print("=" * 70)

if __name__ == '__main__':
    test_checkout_notification()
