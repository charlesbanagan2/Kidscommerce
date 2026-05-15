"""
Shopee-Style Comprehensive Notification System
Handles all order status changes and notifies buyers, sellers, and riders
"""
from datetime import datetime
from flask import current_app
from sqlalchemy import text

def ensure_notification_table(db=None, _sa_text=None):
    """Ensure notification table has all required columns"""
    if db is None:
        from app import db as app_db, _sa_text as app_sa_text
        db = app_db
        _sa_text = app_sa_text

    from sqlalchemy import inspect as sa_inspect

    try:
        inspector = sa_inspect(db.engine)
        cols = {c['name'] for c in inspector.get_columns('notification')}

        stmts = []
        # Only add columns that are NOT in the model (title is now in the model)
        if 'notification_type' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN notification_type VARCHAR(50) DEFAULT 'order'")
        if 'action_url' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN action_url VARCHAR(500)")
        if 'metadata' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN metadata JSON")

        for stmt in stmts:
            db.session.execute(_sa_text(stmt))

        if stmts:
            db.session.commit()
            print(f"[OK] Added {len(stmts)} notification columns")
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Notification table migration error: {e}")


def create_notification(user_id, title, message, notification_type='order',
                       order_id=None, action_url=None, metadata=None):
    """
    Create a notification for a user

    Args:
        user_id: User ID to notify
        title: Notification title
        message: Notification message
        notification_type: Type (order, promotion, product, system)
        order_id: Related order ID
        action_url: URL to navigate when clicked
        metadata: Additional data (JSON)
    """
    from app import db, Notification, socketio

    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            order_id=order_id,
            link=action_url,
            is_read=False,
            created_at=datetime.utcnow()
        )

        # Add metadata if provided
        if metadata and hasattr(notification, 'metadata'):
            notification.metadata = metadata

        db.session.add(notification)
        db.session.commit()

        # Real-time push via SocketIO
        try:
            socketio.emit('notification', {
                'id': notification.id,
                'title': title,
                'message': message,
                'type': notification_type,
                'order_id': order_id,
                'action_url': action_url,
                'created_at': notification.created_at.isoformat()
            }, room=f'user_{user_id}')
        except:
            pass

        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None


# ============= ORDER STATUS NOTIFICATION FUNCTIONS =============

def notify_order_placed(order):
    """Notify when buyer places an order"""
    from app import db, OrderItem
    
    # Notify buyer
    create_notification(
        user_id=order.buyer_id,
        title="Order Placed Successfully",
        message=f"Your order #{order.id} has been placed. Waiting for seller confirmation.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )
    
    # Notify each seller
    sellers = set()
    for item in order.items:
        if item.product.seller_id not in sellers:
            sellers.add(item.product.seller_id)
            create_notification(
                user_id=item.product.seller_id,
                title="New Order Received",
                message=f"You have a new order #{order.id}. Please process it.",
                notification_type='order',
                order_id=order.id,
                action_url=f'/seller/orders/{order.id}'
            )


def notify_order_confirmed(order):
    """Notify when seller confirms order (to_pay -> processing)"""
    create_notification(
        user_id=order.buyer_id,
        title="Order Confirmed",
        message=f"Your order #{order.id} has been confirmed by the seller and is being processed.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )


def notify_order_processing(order):
    """Notify when order is being processed"""
    create_notification(
        user_id=order.buyer_id,
        title="Order Processing",
        message=f"Your order #{order.id} is now being prepared for shipment.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )


def notify_order_ready_for_pickup(order):
    """Notify when order is ready for rider pickup"""
    # Notify buyer
    create_notification(
        user_id=order.buyer_id,
        title="Order Ready for Pickup",
        message=f"Your order #{order.id} is ready and waiting for a rider to pick it up.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )
    
    # Notify all riders (broadcast)
    from app import db, User
    riders = User.query.filter_by(role='rider', status='active').all()
    for rider in riders:
        create_notification(
            user_id=rider.id,
            title="New Delivery Available",
            message=f"Order #{order.id} is ready for pickup. First come, first served!",
            notification_type='order',
            order_id=order.id,
            action_url=f'/rider/orders/available'
        )


def notify_order_accepted_by_rider(order):
    """Notify when rider accepts the order"""
    from app import db, User
    
    # Notify buyer
    rider = db.session.get(User, order.rider_id) if order.rider_id else None
    rider_name = f"{rider.first_name} {rider.last_name}" if rider else "A rider"
    
    create_notification(
        user_id=order.buyer_id,
        title="Rider Assigned",
        message=f"{rider_name} has accepted your order #{order.id} and will deliver it soon.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )
    
    # Notify seller
    for item in order.items:
        create_notification(
            user_id=item.product.seller_id,
            title="Order Picked Up by Rider",
            message=f"Order #{order.id} has been picked up by {rider_name}.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/seller/orders/{order.id}',
            metadata={'rider_id': order.rider_id, 'rider_name': rider_name}
        )
        break  # Only notify once per order


def notify_order_in_transit(order):
    """Notify when order is out for delivery"""
    from app import db, User
    
    rider = db.session.get(User, order.rider_id) if order.rider_id else None
    rider_name = f"{rider.first_name} {rider.last_name}" if rider else "The rider"
    
    create_notification(
        user_id=order.buyer_id,
        title="Out for Delivery",
        message=f"Your order #{order.id} is on the way! {rider_name} is delivering it now.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )


def notify_order_delivered(order):
    """Notify when order is delivered"""
    # Notify buyer
    create_notification(
        user_id=order.buyer_id,
        title="Order Delivered",
        message=f"Your order #{order.id} has been delivered. Please confirm receipt.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )
    
    # Notify seller
    for item in order.items:
        create_notification(
            user_id=item.product.seller_id,
            title="Order Delivered",
            message=f"Order #{order.id} has been delivered to the buyer.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/seller/orders/{order.id}'
        )
        break


def notify_order_completed(order):
    """Notify when buyer confirms receipt (order completed)"""
    from app import db, User
    
    # Notify seller
    for item in order.items:
        create_notification(
            user_id=item.product.seller_id,
            title="Order Completed",
            message=f"Order #{order.id} has been confirmed by the buyer. Payment will be released.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/seller/orders/{order.id}'
        )
        break
    
    # Notify rider
    if order.rider_id:
        create_notification(
            user_id=order.rider_id,
            title="Delivery Completed",
            message=f"Order #{order.id} has been confirmed. Your earnings have been credited.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/rider/earnings'
        )


def notify_order_cancelled(order, cancelled_by='buyer'):
    """Notify when order is cancelled"""
    # Notify buyer
    if cancelled_by != 'buyer':
        create_notification(
            user_id=order.buyer_id,
            title="Order Cancelled",
            message=f"Your order #{order.id} has been cancelled.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/buyer/orders/{order.id}'
        )
    
    # Notify seller
    for item in order.items:
        if cancelled_by != 'seller':
            create_notification(
                user_id=item.product.seller_id,
                title="Order Cancelled",
                message=f"Order #{order.id} has been cancelled by the buyer.",
                notification_type='order',
                order_id=order.id,
                action_url=f'/seller/orders/{order.id}'
            )
        break
    
    # Notify rider if assigned
    if order.rider_id and cancelled_by != 'rider':
        create_notification(
            user_id=order.rider_id,
            title="Delivery Cancelled",
            message=f"Order #{order.id} has been cancelled.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/rider/orders'
        )


# ============= PAYMENT NOTIFICATIONS =============

def notify_payment_confirmed(order):
    """Notify when payment is confirmed"""
    create_notification(
        user_id=order.buyer_id,
        title="Payment Confirmed",
        message=f"Your payment for order #{order.id} has been confirmed.",
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/orders/{order.id}'
    )
    
    # Notify seller
    for item in order.items:
        create_notification(
            user_id=item.product.seller_id,
            title="Payment Received",
            message=f"Payment for order #{order.id} has been confirmed. Please process the order.",
            notification_type='order',
            order_id=order.id,
            action_url=f'/seller/orders/{order.id}'
        )
        break


# ============= RETURN/REFUND NOTIFICATIONS =============

def notify_return_requested(return_request):
    """Notify when buyer requests return/refund"""
    create_notification(
        user_id=return_request.seller_id,
        title="Return/Refund Request",
        message=f"Buyer requested a return/refund for order #{return_request.order_id}.",
        notification_type='order',
        order_id=return_request.order_id,
        action_url=f'/seller/returns/{return_request.id}'
    )


def notify_return_approved(return_request):
    """Notify when seller approves return"""
    create_notification(
        user_id=return_request.buyer_id,
        title="Return Approved",
        message=f"Your return request for order #{return_request.order_id} has been approved.",
        notification_type='order',
        order_id=return_request.order_id,
        action_url=f'/buyer/orders/{return_request.order_id}'
    )


def notify_return_rejected(return_request):
    """Notify when seller rejects return"""
    create_notification(
        user_id=return_request.buyer_id,
        title="Return Rejected",
        message=f"Your return request for order #{return_request.order_id} has been rejected.",
        notification_type='order',
        order_id=return_request.order_id,
        action_url=f'/buyer/orders/{return_request.order_id}'
    )


def notify_refund_processed(return_request, amount):
    """Notify when refund is processed"""
    create_notification(
        user_id=return_request.buyer_id,
        title="Refund Processed",
        message=f"Your refund of ₱{amount:,.2f} for order #{return_request.order_id} has been processed.",
        notification_type='order',
        order_id=return_request.order_id,
        action_url=f'/buyer/wallet'
    )


# ============= PRODUCT NOTIFICATIONS =============

def notify_product_approved(product):
    """Notify seller when product is approved"""
    create_notification(
        user_id=product.seller_id,
        title="Product Approved",
        message=f"Your product '{product.name}' has been approved and is now live!",
        notification_type='product',
        action_url=f'/seller/products/{product.id}'
    )


def notify_product_rejected(product, reason=None):
    """Notify seller when product is rejected"""
    msg = f"Your product '{product.name}' was not approved."
    if reason:
        msg += f" Reason: {reason}"
    
    create_notification(
        user_id=product.seller_id,
        title="Product Rejected",
        message=msg,
        notification_type='product',
        action_url=f'/seller/products/{product.id}'
    )


def notify_low_stock(product):
    """Notify seller when product stock is low"""
    create_notification(
        user_id=product.seller_id,
        title="Low Stock Alert",
        message=f"Your product '{product.name}' is running low on stock ({product.stock} left).",
        notification_type='product',
        action_url=f'/seller/products/{product.id}'
    )


def notify_out_of_stock(product):
    """Notify seller when product is out of stock"""
    create_notification(
        user_id=product.seller_id,
        title="Out of Stock",
        message=f"Your product '{product.name}' is now out of stock. Please restock.",
        notification_type='product',
        action_url=f'/seller/products/{product.id}'
    )


# ============= PROMOTION NOTIFICATIONS =============

def notify_new_promotion(user_id, promo_title, promo_message):
    """Notify user about new promotion"""
    create_notification(
        user_id=user_id,
        title=promo_title,
        message=promo_message,
        notification_type='promotion',
        action_url='/shop'
    )


def notify_coupon_received(user_id, coupon_code, discount_text):
    """Notify user when they receive a coupon"""
    create_notification(
        user_id=user_id,
        title="New Coupon Received!",
        message=f"You've received a coupon: {coupon_code} - {discount_text}",
        notification_type='promotion',
        action_url='/shop'
    )


# ============= SYSTEM NOTIFICATIONS =============

def notify_account_approved(user):
    """Notify user when account is approved"""
    create_notification(
        user_id=user.id,
        title="Account Approved",
        message=f"Welcome! Your {user.role} account has been approved. You can now log in.",
        notification_type='system',
        action_url='/login'
    )


def notify_account_rejected(user, reason=None):
    """Notify user when account is rejected"""
    msg = "Your account registration was not approved."
    if reason:
        msg += f" Reason: {reason}"
    
    create_notification(
        user_id=user.id,
        title="Account Not Approved",
        message=msg,
        notification_type='system'
    )


# ============= HELPER FUNCTIONS =============

def get_user_notifications(user_id, limit=50, unread_only=False):
    """Get notifications for a user"""
    from app import db, Notification
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return notifications


def mark_notification_read(notification_id, user_id):
    """Mark a notification as read"""
    from app import db, Notification
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return True
    return False


def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    from app import db, Notification
    
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()


def get_unread_count(user_id):
    """Get count of unread notifications"""
    from app import Notification
    
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def delete_old_notifications(days=30):
    """Delete notifications older than specified days"""
    from app import db, Notification
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    Notification.query.filter(Notification.created_at < cutoff_date).delete()
    db.session.commit()


# ============= INTEGRATION HOOKS =============

def integrate_with_order_status_change(order, old_status, new_status):
    """
    Main integration point - call this whenever order status changes
    This will automatically send appropriate notifications
    """
    status_handlers = {
        'pending': notify_order_placed,
        'to_pay': notify_order_placed,
        'processing': notify_order_processing,
        'ready_for_pickup': notify_order_ready_for_pickup,
        'accepted_by_rider': notify_order_accepted_by_rider,
        'in_transit': notify_order_in_transit,
        'delivered': notify_order_delivered,
        'completed': notify_order_completed,
        'cancelled': lambda o: notify_order_cancelled(o, 'system')
    }
    
    handler = status_handlers.get(new_status)
    if handler:
        try:
            handler(order)
        except Exception as e:
            print(f"Error sending notification for status {new_status}: {e}")


if __name__ == '__main__':
    print("Shopee-Style Notification System")
    print("=" * 50)
    print("This module provides comprehensive notifications for:")
    print("- Order status changes")
    print("- Payment updates")
    print("- Return/refund requests")
    print("- Product approvals")
    print("- Promotions and coupons")
    print("- System notifications")
