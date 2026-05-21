"""
Test return approval notification
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, ReturnRequest, Notification, push_notification

def test_approval_notification():
    """Test push_notification for return approval"""
    print("\n" + "="*70)
    print("  🧪 TESTING RETURN APPROVAL NOTIFICATION")
    print("="*70)
    
    with app.app_context():
        # Get a refunded return request
        rr = ReturnRequest.query.filter_by(status='refunded').first()
        if not rr:
            print("❌ No refunded return request found")
            return
        
        print(f"\n📦 Return Request #{rr.id}:")
        print(f"   Order ID: {rr.order_id}")
        print(f"   Buyer ID: {rr.buyer_id}")
        print(f"   Status: {rr.status}")
        
        # Count notifications before
        before_count = Notification.query.filter_by(
            user_id=rr.buyer_id,
            order_id=rr.order_id
        ).count()
        print(f"\n📊 Notifications for buyer before test: {before_count}")
        
        # Test sending an approval notification
        print("\n🔔 Sending test approval notification...")
        try:
            push_notification(
                rr.buyer_id,
                f'TEST: Your return request for Order #{rr.order_id} has been approved. The item is now refunded.',
                title='TEST: Return Approved & Refunded',
                link=f'/buyer/orders/{rr.order_id}',
                type='return_approved',
                order_id=rr.order_id
            )
            print("✅ Notification function called successfully")
        except Exception as e:
            print(f"❌ Error calling notification function: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Count notifications after
        after_count = Notification.query.filter_by(
            user_id=rr.buyer_id,
            order_id=rr.order_id
        ).count()
        print(f"📊 Notifications for buyer after test: {after_count}")
        
        if after_count > before_count:
            print(f"✅ SUCCESS: {after_count - before_count} new notification(s) created!")
            
            # Show the new notification
            new_notif = Notification.query.filter_by(
                user_id=rr.buyer_id,
                order_id=rr.order_id
            ).order_by(Notification.created_at.desc()).first()
            
            print(f"\n📬 New Notification:")
            print(f"   Type: {new_notif.type}")
            print(f"   Title: {new_notif.title}")
            print(f"   Message: {new_notif.message}")
        else:
            print("❌ FAILED: No new notification created")
        
        print("\n" + "="*70)

if __name__ == '__main__':
    test_approval_notification()
