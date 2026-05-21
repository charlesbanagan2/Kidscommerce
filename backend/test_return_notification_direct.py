"""
Direct test of return notification functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, ReturnRequest, Notification, push_notification

def test_notification_directly():
    """Test push_notification function directly"""
    print("\n" + "="*70)
    print("  🧪 TESTING NOTIFICATION FUNCTION DIRECTLY")
    print("="*70)
    
    with app.app_context():
        # Get a return request
        rr = ReturnRequest.query.get(4)
        if not rr:
            print("❌ Return request #4 not found")
            return
        
        print(f"\n📦 Return Request #4:")
        print(f"   Order ID: {rr.order_id}")
        print(f"   Buyer ID: {rr.buyer_id}")
        print(f"   Status: {rr.status}")
        print(f"   Rejection Reason: {rr.seller_response_reason}")
        
        # Count notifications before
        before_count = Notification.query.filter_by(
            user_id=rr.buyer_id,
            order_id=rr.order_id
        ).count()
        print(f"\n📊 Notifications for buyer before test: {before_count}")
        
        # Test sending a rejection notification
        print("\n🔔 Sending test rejection notification...")
        try:
            push_notification(
                rr.buyer_id,
                f'TEST: Your return request for Order #{rr.order_id} was rejected. Reason: {rr.seller_response_reason or "No reason provided"}',
                title='TEST: Return Request Rejected',
                link=f'/buyer/orders/{rr.order_id}',
                type='return_rejected',
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
    test_notification_directly()
