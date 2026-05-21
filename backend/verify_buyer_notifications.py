"""
Verification Script: Buyer Notifications for Return/Refund
This script verifies that buyers receive notifications for:
1. Return request submission (confirmation)
2. Return request approval by seller
3. Return request rejection by seller
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, get_data
from datetime import datetime, timedelta

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(msg):
    print(f"✅ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")


def check_notification_setup():
    """Check if notification system is properly configured"""
    print_header("CHECKING NOTIFICATION SYSTEM SETUP")
    
    with app.app_context():
        try:
            from app import Notification, ReturnRequest
            
            # Check if notification table exists
            notif_count = Notification.query.count()
            print_success(f"Notification table exists ({notif_count} records)")
            
            # Check if return_request table exists
            return_count = ReturnRequest.query.count()
            print_success(f"Return request table exists ({return_count} records)")
            
            return True
        except Exception as e:
            print_error(f"Setup check failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def verify_buyer_notification_on_request():
    """Verify buyer gets confirmation when creating return request"""
    print_header("VERIFICATION 1: Buyer Confirmation on Request Submission")
    
    with app.app_context():
        try:
            from app import ReturnRequest, Notification
            
            # Get recent return requests
            returns = ReturnRequest.query.order_by(ReturnRequest.created_at.desc()).limit(5).all()
            
            if not returns:
                print_warning("No return requests found to verify")
                return
            
            for rr in returns:
                buyer_id = rr.buyer_id
                order_id = rr.order_id
                rr_id = rr.id
                
                # Check if buyer received confirmation notification
                buyer_notifs = Notification.query.filter_by(
                    user_id=buyer_id,
                    order_id=order_id
                ).all()
                
                if buyer_notifs:
                    # Look for submission confirmation
                    has_confirmation = any(
                        'submit' in str(n.message or '').lower() or
                        'request' in str(n.title or '').lower()
                        for n in buyer_notifs
                    )
                    
                    if has_confirmation:
                        print_success(f"Return #{rr_id}: Buyer received confirmation ✓")
                    else:
                        print_warning(f"Return #{rr_id}: Buyer has notifications but no confirmation")
                else:
                    print_warning(f"Return #{rr_id}: Buyer has NO notifications")
                    
        except Exception as e:
            print_error(f"Verification failed: {e}")
            import traceback
            traceback.print_exc()


def verify_seller_notification_on_request():
    """Verify seller gets notified when buyer creates return request"""
    print_header("VERIFICATION 2: Seller Notification on Request Creation")
    
    with app.app_context():
        try:
            from app import ReturnRequest, Notification
            
            # Get recent return requests
            returns = ReturnRequest.query.order_by(ReturnRequest.created_at.desc()).limit(5).all()
            
            if not returns:
                print_warning("No return requests found to verify")
                return
            
            for rr in returns:
                seller_id = rr.seller_id
                order_id = rr.order_id
                rr_id = rr.id
                status = rr.status
                
                # Check if seller received notification
                seller_notifs = Notification.query.filter_by(
                    user_id=seller_id,
                    order_id=order_id
                ).all()
                
                if seller_notifs:
                    # Look for return request notification
                    has_request_notif = any(
                        'return' in str(n.message or '').lower() and
                        'request' in str(n.message or '').lower()
                        for n in seller_notifs
                    )
                    
                    if has_request_notif:
                        print_success(f"Return #{rr_id}: Seller received request notification ✓")
                    else:
                        print_warning(f"Return #{rr_id}: Seller has notifications but no request alert")
                else:
                    print_error(f"Return #{rr_id}: Seller has NO notifications ✗")
                    
        except Exception as e:
            print_error(f"Verification failed: {e}")
            import traceback
            traceback.print_exc()


def verify_buyer_notification_on_approval():
    """Verify buyer gets notified when seller approves return"""
    print_header("VERIFICATION 3: Buyer Notification on Approval")
    
    with app.app_context():
        try:
            from app import ReturnRequest, Notification
            
            # Get approved return requests
            returns = ReturnRequest.query.filter_by(status='refunded').order_by(
                ReturnRequest.processed_at.desc()
            ).limit(5).all()
            
            if not returns:
                print_warning("No approved return requests found to verify")
                return
            
            for rr in returns:
                buyer_id = rr.buyer_id
                order_id = rr.order_id
                rr_id = rr.id
                refund_amount = rr.refund_amount
                
                # Check if buyer received approval notification
                buyer_notifs = Notification.query.filter_by(
                    user_id=buyer_id,
                    order_id=order_id
                ).all()
                
                if buyer_notifs:
                    # Look for approval notification
                    has_approval = any(
                        'approv' in str(n.message or '').lower() or
                        'refund' in str(n.message or '').lower()
                        for n in buyer_notifs
                    )
                    
                    if has_approval:
                        print_success(f"Return #{rr_id}: Buyer received APPROVAL notification ✓")
                        print_info(f"  → Refund amount: ₱{refund_amount:.2f}" if refund_amount else "  → Refund amount: N/A")
                    else:
                        print_error(f"Return #{rr_id}: Buyer has notifications but NO APPROVAL ✗")
                else:
                    print_error(f"Return #{rr_id}: Buyer has NO notifications ✗")
                    
        except Exception as e:
            print_error(f"Verification failed: {e}")
            import traceback
            traceback.print_exc()


def verify_buyer_notification_on_rejection():
    """Verify buyer gets notified when seller rejects return"""
    print_header("VERIFICATION 4: Buyer Notification on Rejection ⭐ CRITICAL")
    
    with app.app_context():
        try:
            from app import ReturnRequest, Notification
            
            # Get rejected return requests
            returns = ReturnRequest.query.filter_by(status='rejected').order_by(
                ReturnRequest.processed_at.desc()
            ).limit(5).all()
            
            if not returns:
                print_warning("No rejected return requests found to verify")
                print_info("Create a test rejection to verify this functionality")
                return
            
            for rr in returns:
                buyer_id = rr.buyer_id
                order_id = rr.order_id
                rr_id = rr.id
                rejection_reason = rr.seller_response_reason
                
                # Check if buyer received rejection notification
                buyer_notifs = Notification.query.filter_by(
                    user_id=buyer_id,
                    order_id=order_id
                ).all()
                
                if buyer_notifs:
                    # Look for rejection notification
                    has_rejection = any(
                        'reject' in str(n.message or '').lower()
                        for n in buyer_notifs
                    )
                    
                    if has_rejection:
                        print_success(f"Return #{rr_id}: Buyer received REJECTION notification ✓")
                        print_info(f"  → Rejection reason: {rejection_reason or 'N/A'}")
                        
                        # Check if reason is included in notification
                        has_reason_in_notif = any(
                            rejection_reason and rejection_reason.lower() in str(n.message or '').lower()
                            for n in buyer_notifs
                        ) if rejection_reason else False
                        
                        if has_reason_in_notif:
                            print_success(f"  → Rejection reason included in notification ✓")
                        else:
                            print_warning(f"  → Rejection reason NOT in notification message")
                    else:
                        print_error(f"Return #{rr_id}: Buyer has notifications but NO REJECTION ✗")
                else:
                    print_error(f"Return #{rr_id}: Buyer has NO notifications ✗")
                    
        except Exception as e:
            print_error(f"Verification failed: {e}")
            import traceback
            traceback.print_exc()


def show_notification_summary():
    """Show summary of all notifications"""
    print_header("NOTIFICATION SUMMARY")
    
    with app.app_context():
        try:
            from app import Notification
            
            # Get all return-related notifications
            all_notifs = Notification.query.limit(100).all()
            
            if not all_notifs:
                print_warning("No notifications found in database")
                return
            
            # Filter return-related notifications
            return_notifs = [
                n for n in all_notifs
                if n.type in ['return_request', 'return_approved', 'return_rejected', 'order', 'payment']
                and ('return' in str(n.message or '').lower() or 'refund' in str(n.message or '').lower())
            ]
            
            if not return_notifs:
                print_warning("No return-related notifications found")
                return
            
            print_info(f"Total return-related notifications: {len(return_notifs)}")
            
            # Count by type
            by_type = {}
            for n in return_notifs:
                ntype = n.type or 'unknown'
                by_type[ntype] = by_type.get(ntype, 0) + 1
            
            print("\nNotifications by type:")
            for ntype, count in by_type.items():
                print(f"  • {ntype}: {count}")
            
            # Count by read status
            read_count = sum(1 for n in return_notifs if n.is_read)
            unread_count = len(return_notifs) - read_count
            
            print(f"\nRead status:")
            print(f"  • Read: {read_count}")
            print(f"  • Unread: {unread_count}")
            
            # Show recent notifications
            print("\nRecent notifications (last 5):")
            recent = sorted(return_notifs, key=lambda x: x.created_at or '', reverse=True)[:5]
            for i, n in enumerate(recent, 1):
                print(f"\n  {i}. {n.title or 'No title'}")
                print(f"     Type: {n.type or 'N/A'}")
                print(f"     Message: {(n.message or 'N/A')[:60]}...")
                print(f"     User ID: {n.user_id}")
                print(f"     Order ID: {n.order_id or 'N/A'}")
                print(f"     Read: {'Yes' if n.is_read else 'No'}")
                
        except Exception as e:
            print_error(f"Summary failed: {e}")
            import traceback
            traceback.print_exc()


def show_test_instructions():
    """Show manual testing instructions"""
    print_header("MANUAL TESTING INSTRUCTIONS")
    
    print("""
📱 MOBILE APP TESTING:

1️⃣ TEST BUYER NOTIFICATION ON REQUEST:
   • Login as Buyer
   • Go to completed order
   • Click "Request Return/Refund"
   • Fill form and submit
   • CHECK: Buyer receives confirmation notification
   • CHECK: Seller receives request notification

2️⃣ TEST BUYER NOTIFICATION ON APPROVAL:
   • Login as Seller
   • Go to Returns tab
   • Open pending return request
   • Click "Approve"
   • CHECK: Buyer receives approval notification
   • CHECK: Notification shows refund amount
   • CHECK: Buyer wallet credited

3️⃣ TEST BUYER NOTIFICATION ON REJECTION: ⭐ CRITICAL
   • Login as Seller
   • Go to Returns tab
   • Open pending return request
   • Click "Reject"
   • Enter rejection reason
   • Submit
   • CHECK: Buyer receives rejection notification ✓
   • CHECK: Notification includes rejection reason ✓
   • CHECK: Order status = "completed" ✓

🌐 WEB DASHBOARD TESTING:
   • Repeat above tests using web interface
   • Verify notifications appear in notification bell
   • Verify notification links work correctly

📊 DATABASE VERIFICATION:
   • Run: SELECT * FROM notification WHERE type IN ('return_request', 'return_approved', 'return_rejected') ORDER BY created_at DESC LIMIT 10;
   • Verify notifications created for each action
   • Check user_id matches expected recipient
   • Verify message content includes relevant details
""")


def main():
    print("\n" + "="*70)
    print("  🔔 BUYER NOTIFICATION VERIFICATION SYSTEM")
    print("  Return/Refund Notification Flow Check")
    print("="*70)
    
    # Run all verifications
    if not check_notification_setup():
        print_error("\nSetup check failed. Cannot proceed with verification.")
        return
    
    verify_seller_notification_on_request()
    verify_buyer_notification_on_request()
    verify_buyer_notification_on_approval()
    verify_buyer_notification_on_rejection()
    show_notification_summary()
    show_test_instructions()
    
    print_header("VERIFICATION COMPLETE")
    print("""
✅ EXPECTED RESULTS:
   1. Seller receives notification when buyer requests return ✓
   2. Buyer receives confirmation when request is submitted ✓
   3. Buyer receives notification when seller approves ✓
   4. Buyer receives notification when seller rejects ✓
   5. All notifications include relevant details ✓

⚠️  IF ANY CHECKS FAILED:
   1. Check database for notification records
   2. Verify push_notification function is called
   3. Check SocketIO connection for real-time updates
   4. Review error logs in backend/logs/
   5. Test manually via mobile app

📝 NEXT STEPS:
   1. Review verification results above
   2. Test manually if needed
   3. Check database notifications table
   4. Monitor production logs after deployment
""")


if __name__ == '__main__':
    main()
