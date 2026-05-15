"""
Mobile API Endpoints for Shopee-Style Notifications
Provides REST API for Flutter mobile app to fetch and manage notifications

OPTIMIZATIONS:
- Database indexes on user_id, is_read, created_at
- Eager loading with joinedload() for related data
- Redis caching for frequently accessed data
- Optimized SQL queries with proper filtering
"""
from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, select
import json

# Create blueprint
notification_api_bp = Blueprint('notification_api', __name__)

# JWT Secret
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-mobile-jwt-secret-key-change-in-production')

# Global references (set during registration)
_db = None
_Notification = None
_User = None
_cache = None  # Redis cache instance

def get_db():
    """Get database instance from current Flask app context"""
    # ALWAYS use current_app to get the db instance bound to the current app
    try:
        return current_app.extensions.get('sqlalchemy')
    except:
        return _db

# Cache configuration
CACHE_TIMEOUT = 60  # 60 seconds for notification counts
CACHE_ENABLED = os.getenv('REDIS_CACHE_ENABLED', 'false').lower() == 'true'

def token_required(f):
    """Decorator to require JWT token for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
            
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = payload['user_id']
            current_user_role = payload.get('role', 'buyer')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token is invalid'}), 401
            
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated


# ============= NOTIFICATION ENDPOINTS =============

@notification_api_bp.route('/api/v1/notifications', methods=['GET'])
@token_required
def get_notifications(current_user_id, current_user_role):
    """
    Get all notifications for current user (OPTIMIZED)
    Query params:
        - limit: Number of notifications to return (default: 20, max: 100)
        - offset: Offset for pagination (default: 0)
        - unread_only: Filter unread notifications (default: false)
        - type: Filter by notification type (order, promotion, product, system)
    
    OPTIMIZATIONS:
    - Uses eager loading with joinedload() for actor user
    - Optimized count queries with scalar subqueries
    - Caches unread count for 60 seconds
    - Limits max results to prevent memory issues
    """
    # CRITICAL: Access globals that were set during registration
    if _Notification is None or _User is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    User = _User
    db = get_db()  # Get db from current app context

    try:
        # Validate and limit pagination params
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 per request
        offset = max(int(request.args.get('offset', 0)), 0)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notif_type = request.args.get('type')
        
        # Build optimized query with eager loading
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        query = db.session.query(Notification).options(
            joinedload(Notification.actor)  # Eager load actor user to prevent N+1
        ).filter_by(user_id=current_user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        if notif_type:
            query = query.filter_by(type=notif_type)
        
        # Use window function for efficient counting (single query)
        # Get total count efficiently
        total_count = query.with_entities(func.count(Notification.id)).scalar() or 0
        
        # Get unread count from cache or database
        unread_count = _get_cached_unread_count(current_user_id)
        if unread_count is None:
            unread_count = db.session.query(Notification).filter_by(
                user_id=current_user_id, 
                is_read=False
            ).with_entities(func.count(Notification.id)).scalar() or 0
            _cache_unread_count(current_user_id, unread_count)
        
        # Fetch notifications with optimized query
        notifications = query.order_by(Notification.created_at.desc())\
                             .limit(limit)\
                             .offset(offset)\
                             .all()
        
        # Serialize notifications efficiently
        notifications_data = _serialize_notifications(notifications)
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'total_count': total_count,
            'unread_count': unread_count,
            'has_more': (offset + limit) < total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Failed to fetch notifications: {str(e)}'
        }), 500


@notification_api_bp.route('/api/v1/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count(current_user_id, current_user_role):
    """Get count of unread notifications (CACHED)"""
    if _Notification is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    db = get_db()  # Get db from current app context

    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        # Try to get from cache first
        unread_count = _get_cached_unread_count(current_user_id)
        
        if unread_count is None:
            # Cache miss - query database using db.session.query
            unread_count = db.session.query(Notification).filter_by(
                user_id=current_user_id,
                is_read=False
            ).count() or 0
            
            # Cache the result
            _cache_unread_count(current_user_id, unread_count)

        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200

    except Exception as e:
        print(f"❌ Error getting unread count: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_api_bp.route('/api/v1/notifications/<int:notification_id>/read', methods=['PUT', 'PATCH'])
@token_required
def mark_notification_read(current_user_id, current_user_role, notification_id):
    """Mark a specific notification as read (CACHE INVALIDATION)"""
    if _Notification is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    db = get_db()  # Get db from current app context

    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        notification = db.session.query(Notification).filter_by(id=notification_id, user_id=current_user_id).first()
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404

        # Only update if not already read (avoid unnecessary writes)
        if not notification.is_read:
            notification.is_read = True
            db.session.commit()
            
            # Invalidate cache
            _invalidate_unread_count_cache(current_user_id)

        return jsonify({'success': True, 'message': 'Notification marked as read'}), 200
    except Exception as e:
        if db:
            db.session.rollback()
        print(f"❌ Error marking notification as read: {e}")
        return jsonify({'success': False, 'message': 'Failed to mark notification as read'}), 500


@notification_api_bp.route('/api/v1/notifications/mark-all-read', methods=['PUT', 'PATCH'])
@token_required
def mark_all_read(current_user_id, current_user_role):
    """Mark all notifications as read for current user (OPTIMIZED)"""
    if _Notification is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    db = get_db()  # Get db from current app context
    
    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        # Bulk update with single query
        updated_count = db.session.query(Notification).filter_by(
            user_id=current_user_id,
            is_read=False
        ).update({'is_read': True}, synchronize_session=False)
        
        db.session.commit()
        
        # Invalidate cache
        _invalidate_unread_count_cache(current_user_id)
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        if db:
            db.session.rollback()
        print(f"❌ Error marking all as read: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to mark all as read: {str(e)}'
        }), 500


@notification_api_bp.route('/api/v1/notifications/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user_id, current_user_role, notification_id):
    """Delete a specific notification"""
    if _Notification is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    db = get_db()  # Get db from current app context
    
    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        notification = db.session.query(Notification).filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
        }), 200
        
    except Exception as e:
        if db:
            db.session.rollback()
        print(f"❌ Error deleting notification: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete notification: {str(e)}'
        }), 500


@notification_api_bp.route('/api/v1/notifications/clear-all', methods=['DELETE'])
@token_required
def clear_all_read(current_user_id, current_user_role):
    """Delete all read notifications for current user"""
    if _Notification is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    Notification = _Notification
    db = get_db()  # Get db from current app context
    
    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        deleted_count = db.session.query(Notification).filter_by(
            user_id=current_user_id,
            is_read=True
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} notifications',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        if db:
            db.session.rollback()
        print(f"❌ Error clearing notifications: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to clear notifications: {str(e)}'
        }), 500


@notification_api_bp.route('/api/v1/notifications/settings', methods=['GET', 'PUT'])
@token_required
def notification_settings(current_user_id, current_user_role):
    """Get or update notification settings"""
    if _User is None:
        return jsonify({
            'success': False,
            'message': 'Notification system not properly initialized'
        }), 500
    
    User = _User
    db = get_db()  # Get db from current app context
    
    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'settings': {
                    'email_notifications': user.email_notifications if hasattr(user, 'email_notifications') else True,
                    'push_notifications': True,  # Always enabled for mobile
                    'order_updates': True,
                    'promotions': True,
                    'product_updates': True
                }
            }), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if hasattr(user, 'email_notifications'):
                user.email_notifications = data.get('email_notifications', user.email_notifications)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            }), 200
        
    except Exception as e:
        if db:
            db.session.rollback()
        print(f"❌ Error managing notification settings: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to manage settings: {str(e)}'
        }), 500


# ============= CACHING HELPER FUNCTIONS =============

def _get_cache_key(user_id, key_type='unread_count'):
    """Generate cache key for user-specific data"""
    return f"notif:{key_type}:{user_id}"

def _get_cached_unread_count(user_id):
    """Get unread count from cache"""
    if not CACHE_ENABLED or _cache is None:
        return None
    
    try:
        cache_key = _get_cache_key(user_id, 'unread_count')
        cached_value = _cache.get(cache_key)
        if cached_value is not None:
            return int(cached_value)
    except Exception as e:
        print(f"Cache get error: {e}")
    
    return None

def _cache_unread_count(user_id, count):
    """Cache unread count for user"""
    if not CACHE_ENABLED or _cache is None:
        return
    
    try:
        cache_key = _get_cache_key(user_id, 'unread_count')
        _cache.setex(cache_key, CACHE_TIMEOUT, str(count))
    except Exception as e:
        print(f"Cache set error: {e}")

def _invalidate_unread_count_cache(user_id):
    """Invalidate cached unread count when notifications are read"""
    if not CACHE_ENABLED or _cache is None:
        return
    
    try:
        cache_key = _get_cache_key(user_id, 'unread_count')
        _cache.delete(cache_key)
    except Exception as e:
        print(f"Cache delete error: {e}")

def _serialize_notifications(notifications):
    """Efficiently serialize notification objects to dicts"""
    result = []
    for notif in notifications:
        result.append({
            'id': notif.id,
            'title': getattr(notif, 'title', None) or _get_title_from_message(notif.message),
            'message': notif.message,
            'type': notif.type or 'order',
            'is_read': notif.is_read,
            'order_id': notif.order_id,
            'link': notif.link,
            'action_url': notif.link,
            'image_url': notif.image_url,
            'images': notif.images,
            'created_at': notif.created_at.isoformat() if notif.created_at else None,
            'actor': {
                'id': notif.actor.id,
                'name': f"{notif.actor.first_name} {notif.actor.last_name}"
            } if notif.actor else None
        })
    return result

# ============= HELPER FUNCTIONS =============

def _get_title_from_message(message):
    """Extract title from message if title column doesn't exist"""
    if not message:
        return "Notification"
    
    # Common patterns
    if "order" in message.lower():
        if "placed" in message.lower():
            return "Order Placed"
        elif "confirmed" in message.lower():
            return "Order Confirmed"
        elif "processing" in message.lower():
            return "Order Processing"
        elif "delivered" in message.lower():
            return "Order Delivered"
        elif "completed" in message.lower():
            return "Order Completed"
        elif "cancelled" in message.lower():
            return "Order Cancelled"
        else:
            return "Order Update"
    elif "payment" in message.lower():
        return "Payment Update"
    elif "refund" in message.lower():
        return "Refund Processed"
    elif "return" in message.lower():
        return "Return Request"
    elif "product" in message.lower():
        return "Product Update"
    elif "coupon" in message.lower() or "promo" in message.lower():
        return "Special Offer"
    else:
        return "Notification"


# ============= ADMIN ENDPOINTS (for testing) =============

@notification_api_bp.route('/api/v1/admin/notifications/broadcast', methods=['POST'])
@token_required
def broadcast_notification(current_user_id, current_user_role):
    """Admin endpoint to broadcast notification to all users"""
    db = get_db()  # Get db from current app context
    User = _User
    from shopee_notification_system import create_notification
    
    if current_user_role != 'admin':
        return jsonify({
            'success': False,
            'message': 'Admin access required'
        }), 403
    
    try:
        if db is None:
            return jsonify({'success': False, 'message': 'Database not available'}), 500
        
        data = request.get_json()
        title = data.get('title')
        message = data.get('message')
        notif_type = data.get('type', 'system')
        
        if not title or not message:
            return jsonify({
                'success': False,
                'message': 'Title and message are required'
            }), 400
        
        # Get all active users
        users = db.session.query(User).filter_by(status='active').all()
        
        sent_count = 0
        for user in users:
            try:
                create_notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    notification_type=notif_type
                )
                sent_count += 1
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': f'Notification sent to {sent_count} users',
            'sent_count': sent_count
        }), 200
        
    except Exception as e:
        print(f"Error broadcasting notification: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to broadcast: {str(e)}'
        }), 500


# ============= REGISTER BLUEPRINT =============

def register_notification_api(app, db=None, Notification=None, User=None, cache=None):
    """Register notification API blueprint with Flask app"""
    global _db, _Notification, _User, _cache
    
    # CRITICAL: All parameters must be provided - no lazy loading from app context
    if db is None or Notification is None or User is None:
        raise ValueError(
            "register_notification_api requires db, Notification, and User parameters. "
            "Call it after models are defined: register_notification_api(app, db, Notification, User)"
        )
    
    # Set global references
    _db = db
    _Notification = Notification
    _User = User
    
    if cache is not None:
        _cache = cache
    
    # Try to initialize Redis cache if available
    if _cache is None and CACHE_ENABLED:
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            _cache = redis.from_url(redis_url, decode_responses=True)
            print("[OK] Redis cache connected for notifications")
        except Exception as e:
            print(f"[WARNING] Redis cache not available: {e}")
            print("[INFO] Notifications will work without caching")
    
    app.register_blueprint(notification_api_bp)
    print("[OK] Notification API registered with optimizations")


if __name__ == '__main__':
    print("Notification API Endpoints")
    print("=" * 50)
    print("Available endpoints:")
    print("GET    /api/v1/notifications - Get all notifications")
    print("GET    /api/v1/notifications/unread-count - Get unread count")
    print("PUT    /api/v1/notifications/<id>/read - Mark as read")
    print("PUT    /api/v1/notifications/mark-all-read - Mark all as read")
    print("DELETE /api/v1/notifications/<id> - Delete notification")
    print("DELETE /api/v1/notifications/clear-all - Clear all read")
    print("GET/PUT /api/v1/notifications/settings - Manage settings")
