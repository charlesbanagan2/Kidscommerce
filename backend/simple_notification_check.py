"""
Simple Notification Check Script
Quick verification that notifications are working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("\n" + "="*70)
    print("  🔔 SIMPLE NOTIFICATION CHECK")
    print("="*70)
    
    try:
        from app import app, db, Notification, ReturnRequest, User
        
        with app.app_context():
            # Check notification count
            notif_count = Notification.query.count()
            print(f"\n✅ Total notifications in database: {notif_count}")
            
            # Check return request count
            return_count = ReturnRequest.query.count()
            print(f"✅ Total return requests in database: {return_count}")
            
            # Check recent notifications
            print("\n" + "-"*70)
            print("RECENT NOTIFICATIONS (Last 10):")
            print("-"*70)
            
            recent_notifs = Notification.query.order_by(
                Notification.created_at.desc()
            ).limit(10).all()
            
            if not recent_notifs:
                print("⚠️  No notifications found")
            else:
                for i, n in enumerate(recent_notifs, 1):
                    user = db.session.get(User, n.user_id)
                    user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"
                    user_role = user.role if user else "N/A"
                    
                    print(f"\n{i}. [{n.type or 'N/A'}] {n.title or 'No title'}")
                    print(f"   To: {user_name} ({user_role}) [ID: {n.user_id}]")
                    print(f"   Message: {(n.message or 'N/A')[:70]}...")
                    print(f"   Order ID: {n.order_id or 'N/A'}")
                    print(f"   Read: {'Yes' if n.is_read else 'No'}")
                    print(f"   Created: {n.created_at}")
            
            # Check return requests with notifications
            print("\n" + "-"*70)
            print("RETURN REQUESTS WITH NOTIFICATION STATUS:")
            print("-"*70)
            
            returns = ReturnRequest.query.order_by(
                ReturnRequest.created_at.desc()
            ).limit(5).all()
            
            if not returns:
                print("⚠️  No return requests found")
            else:
                for rr in returns:
                    buyer = db.session.get(User, rr.buyer_id)
                    seller = db.session.get(User, rr.seller_id)
                    
                    buyer_name = f"{buyer.first_name} {buyer.last_name}" if buyer else "Unknown"
                    seller_name = f"{seller.first_name} {seller.last_name}" if seller else "Unknown"
                    
                    # Count notifications for this return
                    buyer_notifs = Notification.query.filter_by(
                        user_id=rr.buyer_id,
                        order_id=rr.order_id
                    ).count()
                    
                    seller_notifs = Notification.query.filter_by(
                        user_id=rr.seller_id,
                        order_id=rr.order_id
                    ).count()
                    
                    print(f"\n📦 Return Request #{rr.id} (Order #{rr.order_id})")
                    print(f"   Status: {rr.status}")
                    print(f"   Buyer: {buyer_name} - Notifications: {buyer_notifs}")
                    print(f"   Seller: {seller_name} - Notifications: {seller_notifs}")
                    
                    if rr.status == 'rejected' and rr.seller_response_reason:
                        print(f"   Rejection Reason: {rr.seller_response_reason}")
                    
                    # Check if expected notifications exist
                    if rr.status == 'submitted':
                        if seller_notifs > 0:
                            print("   ✅ Seller notified about request")
                        else:
                            print("   ❌ Seller NOT notified")
                    
                    elif rr.status == 'rejected':
                        if buyer_notifs > 0:
                            # Check if rejection notification exists
                            rejection_notif = Notification.query.filter(
                                Notification.user_id == rr.buyer_id,
                                Notification.order_id == rr.order_id,
                                Notification.message.ilike('%reject%')
                            ).first()
                            
                            if rejection_notif:
                                print("   ✅ Buyer notified about REJECTION")
                                if rr.seller_response_reason and rr.seller_response_reason.lower() in rejection_notif.message.lower():
                                    print("   ✅ Rejection reason included in notification")
                                else:
                                    print("   ⚠️  Rejection reason NOT in notification")
                            else:
                                print("   ❌ Buyer NOT notified about rejection")
                        else:
                            print("   ❌ Buyer has NO notifications")
                    
                    elif rr.status == 'refunded':
                        if buyer_notifs > 0:
                            approval_notif = Notification.query.filter(
                                Notification.user_id == rr.buyer_id,
                                Notification.order_id == rr.order_id,
                                Notification.message.ilike('%approv%')
                            ).first()
                            
                            if approval_notif:
                                print("   ✅ Buyer notified about APPROVAL")
                            else:
                                print("   ❌ Buyer NOT notified about approval")
                        else:
                            print("   ❌ Buyer has NO notifications")
            
            # Summary
            print("\n" + "="*70)
            print("SUMMARY:")
            print("="*70)
            
            # Count notification types
            return_request_notifs = Notification.query.filter(
                Notification.message.ilike('%return%request%')
            ).count()
            
            rejection_notifs = Notification.query.filter(
                Notification.message.ilike('%reject%')
            ).count()
            
            approval_notifs = Notification.query.filter(
                Notification.message.ilike('%approv%')
            ).count()
            
            print(f"\n📊 Notification Statistics:")
            print(f"   • Total notifications: {notif_count}")
            print(f"   • Return request notifications: {return_request_notifs}")
            print(f"   • Rejection notifications: {rejection_notifs}")
            print(f"   • Approval notifications: {approval_notifs}")
            
            print(f"\n📦 Return Request Statistics:")
            print(f"   • Total return requests: {return_count}")
            
            submitted = ReturnRequest.query.filter_by(status='submitted').count()
            rejected = ReturnRequest.query.filter_by(status='rejected').count()
            refunded = ReturnRequest.query.filter_by(status='refunded').count()
            
            print(f"   • Submitted: {submitted}")
            print(f"   • Rejected: {rejected}")
            print(f"   • Refunded: {refunded}")
            
            print("\n" + "="*70)
            print("✅ CHECK COMPLETE")
            print("="*70)
            
            print("\n📝 Next Steps:")
            print("1. If no notifications found, test manually via mobile app")
            print("2. Create a return request as buyer")
            print("3. Reject it as seller with a reason")
            print("4. Run this script again to verify notifications were created")
            print("\n")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
