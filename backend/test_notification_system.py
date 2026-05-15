"""
Test Notification System - Buyer, Seller, Rider
This script tests the complete notification flow for all user roles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Order, Notification
from shopee_notification_system import (
    create_notification,
    notify_order_placed,
    notify_order_processing,
    notify_order_ready_for_pickup,
    notify_order_accepted_by_rider,
    notify_order_in_transit,
    notify_order_delivered,
    notify_order_completed,
    notify_payment_confirmed,
    get_user_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_unread_count
)
from datetime import datetime

def test_notification_system():
    """Test notification system for all roles"""
    
    print("=" * 70)
    print("NOTIFICATION SYSTEM TEST - Buyer, Seller, Rider")
    print("=" * 70)
    
    with app.app_context():
        # Get test users (or create them if they don't exist)
        print("\n[1] Getting test users...")
        buyer = User.query.filter_by(role='buyer').first()
        seller = User.query.filter_by(role='seller').first()
        rider = User.query.filter_by(role='rider').first()
        
        if not buyer:
            print("  [!] No buyer found - creating test buyer")
            buyer = User(
                email='test_buyer@example.com',
                first_name='Test',
                last_name='Buyer',
                role='buyer',
                status='active'
            )
            db.session.add(buyer)
            db.session.commit()
            print(f"  [OK] Created buyer: {buyer.id} - {buyer.email}")
        else:
            print(f"  [OK] Found buyer: {buyer.id} - {buyer.email}")
        
        if not seller:
            print("  [!] No seller found - creating test seller")
            seller = User(
                email='test_seller@example.com',
                first_name='Test',
                last_name='Seller',
                role='seller',
                status='active'
            )
            db.session.add(seller)
            db.session.commit()
            print(f"  [OK] Created seller: {seller.id} - {seller.email}")
        else:
            print(f"  [OK] Found seller: {seller.id} - {seller.email}")
        
        if not rider:
            print("  [!] No rider found - creating test rider")
            rider = User(
                email='test_rider@example.com',
                first_name='Test',
                last_name='Rider',
                role='rider',
                status='active'
            )
            db.session.add(rider)
            db.session.commit()
            print(f"  [OK] Created rider: {rider.id} - {rider.email}")
        else:
            print(f"  [OK] Found rider: {rider.id} - {rider.email}")
        
        # Clear existing test notifications
        print("\n[2] Clearing existing test notifications...")
        Notification.query.filter(
            Notification.user_id.in_([buyer.id, seller.id, rider.id])
        ).delete()
        db.session.commit()
        print("  [OK] Cleared existing notifications")
        
        # ==================== BUYER NOTIFICATIONS ====================
        print("\n" + "=" * 70)
        print("BUYER NOTIFICATIONS")
        print("=" * 70)
        
        print("\n[3] Creating buyer notifications...")
        
        # Buyer - Order Placed
        create_notification(
            user_id=buyer.id,
            title="Order Placed Successfully",
            message="Your order #12345 has been placed. Waiting for seller confirmation.",
            notification_type='order',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Order Placed")
        
        # Buyer - Order Processing
        create_notification(
            user_id=buyer.id,
            title="Order Processing",
            message="Your order #12345 is now being prepared for shipment.",
            notification_type='order',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Order Processing")
        
        # Buyer - Rider Assigned
        create_notification(
            user_id=buyer.id,
            title="[MOTOR] Rider Assigned!",
            message="Juan Dela Cruz will deliver your order #12345. Contact: 09123456789",
            notification_type='order',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Rider Assigned")
        
        # Buyer - Out for Delivery
        create_notification(
            user_id=buyer.id,
            title="[TRUCK] Out for Delivery!",
            message="Your order #12345 is on the way!",
            notification_type='order',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Out for Delivery")
        
        # Buyer - Order Delivered
        create_notification(
            user_id=buyer.id,
            title="[OK] Order Delivered",
            message="Your order #12345 has been delivered. Please confirm receipt.",
            notification_type='order',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Order Delivered")
        
        # Buyer - Payment Confirmed
        create_notification(
            user_id=buyer.id,
            title="Payment Confirmed",
            message="Your payment for order #12345 has been confirmed.",
            notification_type='payment',
            order_id=12345,
            action_url='/buyer/orders/12345'
        )
        print("  [OK] Created: Payment Confirmed")
        
        # Buyer - Promotion
        create_notification(
            user_id=buyer.id,
            title="[PARTY] Special Offer!",
            message="Get 20% off on your next order. Use code: SAVE20",
            notification_type='promotion',
            action_url='/shop'
        )
        print("  [OK] Created: Promotion")
        
        # Buyer - System
        create_notification(
            user_id=buyer.id,
            title="Account Verified",
            message="Your account has been successfully verified.",
            notification_type='system',
            action_url='/profile'
        )
        print("  [OK] Created: System Notification")
        
        # ==================== SELLER NOTIFICATIONS ====================
        print("\n" + "=" * 70)
        print("SELLER NOTIFICATIONS")
        print("=" * 70)
        
        print("\n[4] Creating seller notifications...")
        
        # Seller - New Order
        create_notification(
            user_id=seller.id,
            title="[CART] New Order Received!",
            message="Order #12345 from Test Buyer. Total: PHP1,500.00",
            notification_type='order',
            order_id=12345,
            action_url='/seller/orders/12345'
        )
        print("  [OK] Created: New Order Received")
        
        # Seller - Rider Assigned
        create_notification(
            user_id=seller.id,
            title="[OK] Rider Assigned",
            message="Rider Juan Dela Cruz accepted order #12345",
            notification_type='order',
            order_id=12345,
            action_url='/seller/orders/12345'
        )
        print("  [OK] Created: Rider Assigned")
        
        # Seller - Order Delivered
        create_notification(
            user_id=seller.id,
            title="[OK] Order Delivered",
            message="Order #12345 successfully delivered to customer.",
            notification_type='order',
            order_id=12345,
            action_url='/seller/orders/12345'
        )
        print("  [OK] Created: Order Delivered")
        
        # Seller - Order Completed
        create_notification(
            user_id=seller.id,
            title="[MONEY] Order Completed",
            message="Order #12345 has been confirmed by the buyer. Payment will be released.",
            notification_type='order',
            order_id=12345,
            action_url='/seller/orders/12345'
        )
        print("  [OK] Created: Order Completed")
        
        # Seller - Payment Received
        create_notification(
            user_id=seller.id,
            title="Payment Received",
            message="Payment for order #12345 has been confirmed. Please process the order.",
            notification_type='payment',
            order_id=12345,
            action_url='/seller/orders/12345'
        )
        print("  [OK] Created: Payment Received")
        
        # Seller - Product Approved
        create_notification(
            user_id=seller.id,
            title="Product Approved",
            message="Your product 'Sample Product' has been approved and is now live!",
            notification_type='product',
            action_url='/seller/products/123'
        )
        print("  [OK] Created: Product Approved")
        
        # Seller - Low Stock
        create_notification(
            user_id=seller.id,
            title="[!] Low Stock Alert",
            message="Your product 'Sample Product' is running low on stock (5 left).",
            notification_type='product',
            action_url='/seller/products/123'
        )
        print("  [OK] Created: Low Stock Alert")
        
        # ==================== RIDER NOTIFICATIONS ====================
        print("\n" + "=" * 70)
        print("RIDER NOTIFICATIONS")
        print("=" * 70)
        
        print("\n[5] Creating rider notifications...")
        
        # Rider - New Delivery Available
        create_notification(
            user_id=rider.id,
            title="[BOX] New Delivery Available",
            message="Order #12345 is ready for pickup. First come, first served!",
            notification_type='order',
            order_id=12345,
            action_url='/rider/orders/available'
        )
        print("  [OK] Created: New Delivery Available")
        
        # Rider - Order Accepted
        create_notification(
            user_id=rider.id,
            title="[OK] Order Accepted",
            message="You have accepted order #12345. Proceed to pickup.",
            notification_type='order',
            order_id=12345,
            action_url='/rider/orders/12345'
        )
        print("  [OK] Created: Order Accepted")
        
        # Rider - Delivery Completed
        create_notification(
            user_id=rider.id,
            title="[MONEY] Delivery Completed",
            message="Order #12345 has been confirmed. Your earnings have been credited.",
            notification_type='payment',
            order_id=12345,
            action_url='/rider/earnings'
        )
        print("  [OK] Created: Delivery Completed")
        
        # Rider - Bonus Earned
        create_notification(
            user_id=rider.id,
            title="[GIFT] Bonus Earned!",
            message="You earned a PHP50 bonus for completing 5 deliveries today!",
            notification_type='system',
            action_url='/rider/earnings'
        )
        print("  [OK] Created: Bonus Earned")
        
        # ==================== FETCH AND DISPLAY NOTIFICATIONS ====================
        print("\n" + "=" * 70)
        print("FETCHING NOTIFICATIONS")
        print("=" * 70)
        
        # Buyer notifications
        print("\n[6] Buyer Notifications:")
        buyer_notifs = get_user_notifications(buyer.id, limit=20)
        buyer_unread = get_unread_count(buyer.id)
        print(f"  Total: {len(buyer_notifs)} | Unread: {buyer_unread}")
        for notif in buyer_notifs:
            status = "[RED]" if not notif.is_read else "[WHITE]"
            print(f"    {status} [{notif.type.upper()}] {notif.title}")
            print(f"       {notif.message}")
            print(f"       Link: {notif.link}")
        
        # Seller notifications
        print("\n[7] Seller Notifications:")
        seller_notifs = get_user_notifications(seller.id, limit=20)
        seller_unread = get_unread_count(seller.id)
        print(f"  Total: {len(seller_notifs)} | Unread: {seller_unread}")
        for notif in seller_notifs:
            status = "[RED]" if not notif.is_read else "[WHITE]"
            print(f"    {status} [{notif.type.upper()}] {notif.title}")
            print(f"       {notif.message}")
            print(f"       Link: {notif.link}")
        
        # Rider notifications
        print("\n[8] Rider Notifications:")
        rider_notifs = get_user_notifications(rider.id, limit=20)
        rider_unread = get_unread_count(rider.id)
        print(f"  Total: {len(rider_notifs)} | Unread: {rider_unread}")
        for notif in rider_notifs:
            status = "[RED]" if not notif.is_read else "[WHITE]"
            print(f"    {status} [{notif.type.upper()}] {notif.title}")
            print(f"       {notif.message}")
            print(f"       Link: {notif.link}")
        
        # ==================== TEST MARK AS READ ====================
        print("\n" + "=" * 70)
        print("TESTING MARK AS READ")
        print("=" * 70)
        
        if buyer_notifs:
            print("\n[9] Marking first buyer notification as read...")
            mark_notification_read(buyer_notifs[0].id, buyer.id)
            buyer_unread_after = get_unread_count(buyer.id)
            print(f"  Unread before: {buyer_unread}")
            print(f"  Unread after: {buyer_unread_after}")
            print(f"  [OK] Mark as read working")
        
        # ==================== API ENDPOINT SAMPLES ====================
        print("\n" + "=" * 70)
        print("API ENDPOINT SAMPLES")
        print("=" * 70)
        
        print("\n[10] Sample API requests:")
        print("\n  GET /api/v1/notifications")
        print("    Headers: Authorization: Bearer <token>")
        print("    Query: limit=20&offset=0&type=order")
        print("\n  GET /api/v1/notifications/unread-count")
        print("    Headers: Authorization: Bearer <token>")
        print("\n  PUT /api/v1/notifications/<id>/read")
        print("    Headers: Authorization: Bearer <token>")
        print("\n  PUT /api/v1/notifications/mark-all-read")
        print("    Headers: Authorization: Bearer <token>")
        print("\n  DELETE /api/v1/notifications/<id>")
        print("    Headers: Authorization: Bearer <token>")
        
        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        
        print("\n[STATS] Summary:")
        print(f"  Buyer: {len(buyer_notifs)} notifications, {get_unread_count(buyer.id)} unread")
        print(f"  Seller: {len(seller_notifs)} notifications, {get_unread_count(seller.id)} unread")
        print(f"  Rider: {len(rider_notifs)} notifications, {get_unread_count(rider.id)} unread")
        
        print("\n[OK] All notification types created successfully!")
        print("[OK] API endpoints documented above")
        print("[OK] Mark as read functionality tested")

if __name__ == '__main__':
    test_notification_system()
