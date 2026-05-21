"""
Test script to verify return/refund notification system
Run this to check if all notifications are working correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, push_notification, get_data

def test_notification_function():
    """Test if push_notification function works with correct parameters"""
    print("\n" + "="*60)
    print("🧪 TESTING NOTIFICATION FUNCTION")
    print("="*60)
    
    with app.app_context():
        try:
            # Test 1: Basic notification
            print("\n1️⃣ Testing basic notification...")
            push_notification(
                user_id=1,
                message="Test notification message",
                title="Test Title",
                type="test"
            )
            print("✅ Basic notification - OK")
            
            # Test 2: Return request notification (Buyer → Seller)
            print("\n2️⃣ Testing return request notification (Buyer → Seller)...")
            push_notification(
                user_id=1,
                message="New return request for Order #123",
                title="Return/Refund Request",
                link="/seller/returns/1",
                type="return_request",
                order_id=123
            )
            print("✅ Return request notification - OK")
            
            # Test 3: Return rejection notification (Seller → Buyer)
            print("\n3️⃣ Testing return rejection notification (Seller → Buyer)...")
            push_notification(
                user_id=1,
                message="Your return request for Order #123 was rejected. Reason: Item already used",
                title="Return Request Rejected",
                link="/buyer/orders/123",
                type="return_rejected",
                order_id=123
            )
            print("✅ Return rejection notification - OK")
            
            # Test 4: Return approval notification (Seller → Buyer)
            print("\n4️⃣ Testing return approval notification (Seller → Buyer)...")
            push_notification(
                user_id=1,
                message="Your return request for Order #123 has been approved. The item is now refunded.",
                title="Return Approved & Refunded",
                link="/buyer/orders/123",
                type="return_approved",
                order_id=123
            )
            print("✅ Return approval notification - OK")
            
            print("\n" + "="*60)
            print("✅ ALL NOTIFICATION TESTS PASSED!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


def check_recent_notifications():
    """Check recent notifications in database"""
    print("\n" + "="*60)
    print("📊 CHECKING RECENT NOTIFICATIONS IN DATABASE")
    print("="*60)
    
    with app.app_context():
        try:
            # Get recent notifications
            notifications = get_data(
                'notification',
                filters={},
                order_by='created_at',
                limit=10
            )
            
            if not notifications:
                print("\n⚠️ No notifications found in database")
                return
            
            print(f"\n📋 Found {len(notifications)} recent notifications:\n")
            
            for i, notif in enumerate(notifications, 1):
                print(f"{i}. ID: {notif.get('id')}")
                print(f"   User ID: {notif.get('user_id')}")
                print(f"   Title: {notif.get('title', 'N/A')}")
                print(f"   Message: {notif.get('message', 'N/A')[:60]}...")
                print(f"   Type: {notif.get('type', 'N/A')}")
                print(f"   Order ID: {notif.get('order_id', 'N/A')}")
                print(f"   Read: {notif.get('is_read', False)}")
                print(f"   Created: {notif.get('created_at', 'N/A')}")
                print()
            
        except Exception as e:
            print(f"\n❌ ERROR checking notifications: {e}")
            import traceback
            traceback.print_exc()


def check_return_requests():
    """Check recent return requests"""
    print("\n" + "="*60)
    print("📦 CHECKING RECENT RETURN REQUESTS")
    print("="*60)
    
    with app.app_context():
        try:
            # Get recent return requests
            returns = get_data(
                'return_request',
                filters={},
                order_by='created_at',
                limit=5
            )
            
            if not returns:
                print("\n⚠️ No return requests found in database")
                return
            
            print(f"\n📋 Found {len(returns)} recent return requests:\n")
            
            for i, rr in enumerate(returns, 1):
                print(f"{i}. Return Request ID: {rr.get('id')}")
                print(f"   Order ID: {rr.get('order_id')}")
                print(f"   Buyer ID: {rr.get('buyer_id')}")
                print(f"   Seller ID: {rr.get('seller_id')}")
                print(f"   Status: {rr.get('status')}")
                print(f"   Reason: {rr.get('reason', 'N/A')}")
                print(f"   Seller Response: {rr.get('seller_response_reason', 'N/A')}")
                print(f"   Created: {rr.get('created_at', 'N/A')}")
                print()
            
        except Exception as e:
            print(f"\n❌ ERROR checking return requests: {e}")
            import traceback
            traceback.print_exc()


def verify_notification_flow():
    """Verify complete notification flow"""
    print("\n" + "="*60)
    print("🔍 VERIFYING NOTIFICATION FLOW")
    print("="*60)
    
    with app.app_context():
        try:
            # Check if we have return requests with notifications
            returns = get_data('return_request', filters={}, limit=5)
            
            if not returns:
                print("\n⚠️ No return requests to verify")
                return
            
            for rr in returns:
                rr_id = rr.get('id')
                order_id = rr.get('order_id')
                buyer_id = rr.get('buyer_id')
                seller_id = rr.get('seller_id')
                status = rr.get('status')
                
                print(f"\n📦 Return Request #{rr_id} (Order #{order_id})")
                print(f"   Status: {status}")
                
                # Check buyer notifications
                buyer_notifs = get_data(
                    'notification',
                    filters={'user_id': buyer_id, 'order_id': order_id}
                )
                print(f"   Buyer notifications: {len(buyer_notifs) if buyer_notifs else 0}")
                
                # Check seller notifications
                seller_notifs = get_data(
                    'notification',
                    filters={'user_id': seller_id, 'order_id': order_id}
                )
                print(f"   Seller notifications: {len(seller_notifs) if seller_notifs else 0}")
                
                # Verify expected notifications based on status
                if status == 'submitted':
                    if seller_notifs and len(seller_notifs) > 0:
                        print("   ✅ Seller notified about request")
                    else:
                        print("   ⚠️ Seller NOT notified about request")
                
                elif status == 'rejected':
                    if buyer_notifs and len(buyer_notifs) > 0:
                        # Check if rejection notification exists
                        has_rejection = any('reject' in str(n.get('message', '')).lower() for n in buyer_notifs)
                        if has_rejection:
                            print("   ✅ Buyer notified about rejection")
                        else:
                            print("   ⚠️ Buyer NOT notified about rejection")
                    else:
                        print("   ⚠️ Buyer has NO notifications")
                
                elif status == 'refunded':
                    if buyer_notifs and len(buyer_notifs) > 0:
                        # Check if approval notification exists
                        has_approval = any('approv' in str(n.get('message', '')).lower() for n in buyer_notifs)
                        if has_approval:
                            print("   ✅ Buyer notified about approval")
                        else:
                            print("   ⚠️ Buyer NOT notified about approval")
                    else:
                        print("   ⚠️ Buyer has NO notifications")
            
        except Exception as e:
            print(f"\n❌ ERROR verifying flow: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔔 RETURN/REFUND NOTIFICATION SYSTEM TEST")
    print("="*60)
    
    # Run tests
    test_notification_function()
    check_recent_notifications()
    check_return_requests()
    verify_notification_flow()
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)
    print("\n📝 Next Steps:")
    print("1. Check the output above for any ⚠️ warnings")
    print("2. Test manually via mobile app:")
    print("   - Create return request as buyer")
    print("   - Check seller receives notification")
    print("   - Reject return as seller")
    print("   - Check buyer receives notification")
    print("3. Monitor database for new notifications")
    print("="*60 + "\n")
