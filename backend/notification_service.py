# Notification System - Database Model & Service

from datetime import datetime
from flask_socketio import emit
import logging

logger = logging.getLogger(__name__)

# Use the existing Notification model from app.py
# This file only contains helper functions


class NotificationService:
    """Centralized notification service for all roles"""

    @staticmethod
    def create_notification(user_id, title, message, notification_type,
                          order_id=None, action_url=None, metadata=None):
        """Create and save notification to database"""
        try:
            # Import from app to avoid circular import
            import sys
            db = sys.modules['app'].db
            Notification = sys.modules['app'].Notification
            socketio = sys.modules['app'].socketio

            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,  # Use 'type' column, not 'notification_type'
                order_id=order_id,
                link=action_url,  # Use 'link' column, not 'action_url'
                is_read=False
            )
            if metadata:
                # Store metadata if column exists
                if hasattr(notif, 'metadata'):
                    notif.metadata = metadata

            db.session.add(notif)
            db.session.commit()

            # Emit real-time notification via SocketIO
            # Standardize room naming to 'user_{user_id}'
            try:
                socketio.emit('notification', {
                    'id': notif.id,
                    'title': title,
                    'message': message,
                    'type': notification_type,
                    'order_id': order_id,
                    'action_url': action_url,
                    'created_at': notif.created_at.isoformat() if notif.created_at else None
                }, room=f'user_{user_id}')
            except Exception as e:
                logger.error(f"Error emitting real-time notification: {e}")

            logger.info(f"Notification created: {notification_type} for user {user_id}")
            return notif
        except Exception as e:
            import sys
            db = sys.modules['app'].db
            db.session.rollback()
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def notify_new_order(order):
        """Buyer places order → Notify Seller"""
        seller_id = order.items[0].product.seller_id if order.items else None
        if not seller_id:
            return

        NotificationService.create_notification(
            user_id=seller_id,
            title='🛒 New Order Received!',
            message=f'Order #{order.id} from {order.buyer.first_name}. Total: ₱{order.total_amount:.2f}',
            notification_type='new_order',
            order_id=order.id,
            action_url=f'/seller/order/{order.id}',
            metadata={'order_total': float(order.total_amount), 'buyer_name': order.buyer.first_name}
        )
    
    @staticmethod
    def notify_order_processing(order):
        """Seller processes order → Notify Buyer"""
        NotificationService.create_notification(
            user_id=order.buyer_id,
            title='⚙️ Order Processing',
            message=f'Your order #{order.id} is now being processed by the seller.',
            notification_type='order_processing',
            order_id=order.id,
            action_url=f'/buyer/order/{order.id}',
            metadata={'order_id': order.id}
        )
    
    @staticmethod
    def notify_ready_for_pickup(order):
        """Seller marks ready → Notify all Riders"""
        from models import User
        riders = User.query.filter_by(role='rider', is_active=True).all()
        
        for rider in riders:
            NotificationService.create_notification(
                user_id=rider.id,
                title='📦 New Delivery Available',
                message=f'Order #{order.id} is ready for pickup. First come, first served!',
                notification_type='new_delivery',
                order_id=order.id,
                action_url=f'/rider/orders/available',
                metadata={
                    'order_id': order.id,
                    'earnings': float(order.shipping_fee),
                    'pickup_address': order.items[0].product.seller.business_address if order.items else None
                }
            )
    
    @staticmethod
    def notify_rider_assigned(order):
        """Rider accepts → Notify Buyer & Seller"""
        if not order.rider_id:
            return

        rider = order.rider
        rider_name = f"{rider.first_name} {rider.last_name}"

        # Notify Buyer
        NotificationService.create_notification(
            user_id=order.buyer_id,
            title='🏍️ Rider Assigned!',
            message=f'{rider_name} will deliver your order #{order.id}. Contact: {rider.phone or "N/A"}',
            notification_type='rider_assigned',
            order_id=order.id,
            action_url=f'/buyer/order/{order.id}',
            metadata={
                'rider_name': rider_name,
                'rider_phone': rider.phone,
                'order_id': order.id
            }
        )

        # Notify Seller
        seller_id = order.items[0].product.seller_id if order.items else None
        if seller_id:
            NotificationService.create_notification(
                user_id=seller_id,
                title='✅ Rider Assigned',
                message=f'Rider {rider_name} accepted order #{order.id}',
                notification_type='rider_assigned',
                order_id=order.id,
                action_url=f'/seller/order/{order.id}',
                metadata={'rider_name': rider_name, 'order_id': order.id}
            )

    @staticmethod
    def notify_out_for_delivery(order):
        """Rider marks out for delivery → Notify Buyer"""
        NotificationService.create_notification(
            user_id=order.buyer_id,
            title='🚚 Out for Delivery!',
            message=f'Your order #{order.id} is on the way!',
            notification_type='out_for_delivery',
            order_id=order.id,
            action_url=f'/buyer/order/{order.id}',
            metadata={'order_id': order.id}
        )

    @staticmethod
    def notify_delivered(order):
        """Rider marks delivered → Notify Buyer & Seller"""
        # Notify Buyer
        NotificationService.create_notification(
            user_id=order.buyer_id,
            title='✅ Order Delivered!',
            message=f'Your order #{order.id} has been delivered. Please confirm receipt.',
            notification_type='order_delivered',
            order_id=order.id,
            action_url=f'/buyer/order/{order.id}',
            metadata={'order_id': order.id}
        )

        # Notify Seller
        seller_id = order.items[0].product.seller_id if order.items else None
        if seller_id:
            NotificationService.create_notification(
                user_id=seller_id,
                title='✅ Order Delivered',
                message=f'Order #{order.id} successfully delivered to customer.',
                notification_type='order_delivered',
                order_id=order.id,
                action_url=f'/seller/order/{order.id}',
                metadata={'order_id': order.id}
            )

    @staticmethod
    def notify_order_completed(order):
        """Buyer confirms receipt → Notify Rider with earnings"""
        if not order.rider_id:
            return

        NotificationService.create_notification(
            user_id=order.rider_id,
            title='💰 Delivery Completed!',
            message=f'Order #{order.id} completed. ₱{order.shipping_fee:.2f} added to your wallet.',
            notification_type='delivery_completed',
            order_id=order.id,
            action_url=f'/rider/earnings',
            metadata={
                'order_id': order.id,
                'earnings': float(order.shipping_fee)
            }
        )

    @staticmethod
    def get_unread_count(user_id):
        """Get unread notification count for user"""
        import sys
        Notification = sys.modules['app'].Notification
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        import sys
        db = sys.modules['app'].db
        Notification = sys.modules['app'].Notification
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            if hasattr(notif, 'read_at'):
                notif.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for user"""
        import sys
        db = sys.modules['app'].db
        Notification = sys.modules['app'].Notification
        update_data = {'is_read': True}
        Notification = sys.modules['app'].Notification
        if hasattr(Notification, 'read_at'):
            update_data['read_at'] = datetime.utcnow()
        Notification.query.filter_by(user_id=user_id, is_read=False).update(update_data)
        db.session.commit()
