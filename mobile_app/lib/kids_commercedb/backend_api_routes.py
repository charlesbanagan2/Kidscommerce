"""
BACKEND API ROUTES FOR NOTIFICATIONS AND CHAT
==============================================

Add these routes to your Flask/Express backend server.

NOTIFICATIONS ENDPOINTS:
------------------------

1. GET /api/v1/notifications
   - Get all notifications for logged-in user
   - Auth: Required
   - Response: { success: true, notifications: [...] }

2. GET /api/v1/notifications/unread-count
   - Get count of unread notifications
   - Auth: Required
   - Response: { success: true, unread_count: 5 }

3. PUT /api/v1/notifications/:id/read
   - Mark specific notification as read
   - Auth: Required
   - Response: { success: true }

4. PUT /api/v1/notifications/mark-all-read
   - Mark all notifications as read
   - Auth: Required
   - Response: { success: true }

CHAT ENDPOINTS:
---------------

1. GET /api/v1/chat/conversations
   - Get all chat conversations for user
   - Auth: Required
   - Response: { success: true, conversations: [...] }

2. GET /api/v1/chat/messages/:peerId?is_seller=true
   - Get messages with specific peer
   - Auth: Required
   - Query: is_seller (boolean)
   - Response: { success: true, messages: [...] }

3. POST /api/v1/chat/send
   - Send a new message
   - Auth: Required
   - Body: { recipient_id, content, is_seller }
   - Response: { success: true, message: {...} }

4. GET /api/v1/chat/unread-count
   - Get count of unread messages
   - Auth: Required
   - Response: { success: true, unread_count: 3 }

PYTHON FLASK IMPLEMENTATION:
-----------------------------
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)
chat_bp = Blueprint('chat', __name__)

# Auth decorator (adjust based on your auth system)
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        try:
            # Decode JWT and get user_id
            payload = jwt.decode(token, 'YOUR_SECRET_KEY', algorithms=['HS256'])
            request.user_id = payload['user_id']
        except:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ============ NOTIFICATIONS ROUTES ============

@notifications_bp.route('/api/v1/notifications', methods=['GET'])
@require_auth
def get_notifications():
    """Get all notifications for user"""
    user_id = request.user_id
    
    query = """
        SELECT id, type, title, message, data, is_read, created_at, read_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 50
    """
    
    notifications = db.execute(query, (user_id,))
    
    return jsonify({
        'success': True,
        'notifications': notifications
    })

@notifications_bp.route('/api/v1/notifications/unread-count', methods=['GET'])
@require_auth
def get_unread_count():
    """Get unread notifications count"""
    user_id = request.user_id
    
    query = """
        SELECT COUNT(*) as count
        FROM notifications
        WHERE user_id = %s AND is_read = FALSE
    """
    
    result = db.execute_one(query, (user_id,))
    count = result['count'] if result else 0
    
    return jsonify({
        'success': True,
        'unread_count': count
    })

@notifications_bp.route('/api/v1/notifications/<int:notification_id>/read', methods=['PUT'])
@require_auth
def mark_notification_read(notification_id):
    """Mark notification as read"""
    user_id = request.user_id
    
    query = """
        UPDATE notifications
        SET is_read = TRUE, read_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
    """
    
    db.execute(query, (notification_id, user_id))
    
    return jsonify({'success': True})

@notifications_bp.route('/api/v1/notifications/mark-all-read', methods=['PUT'])
@require_auth
def mark_all_read():
    """Mark all notifications as read"""
    user_id = request.user_id
    
    query = """
        UPDATE notifications
        SET is_read = TRUE, read_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND is_read = FALSE
    """
    
    db.execute(query, (user_id,))
    
    return jsonify({'success': True})

# ============ CHAT ROUTES ============

@chat_bp.route('/api/v1/chat/conversations', methods=['GET'])
@require_auth
def get_conversations():
    """Get all conversations for user"""
    user_id = request.user_id
    
    query = """
        SELECT 
            c.id,
            CASE 
                WHEN c.buyer_id = %s THEN c.seller_id
                ELSE c.buyer_id
            END as peer_id,
            CASE 
                WHEN c.buyer_id = %s THEN u_seller.first_name || ' ' || u_seller.last_name
                ELSE u_buyer.first_name || ' ' || u_buyer.last_name
            END as peer_name,
            c.last_message,
            c.last_message_time,
            (SELECT COUNT(*) FROM chat_messages 
             WHERE conversation_id = c.id 
             AND recipient_id = %s 
             AND is_read = FALSE) as unread_count
        FROM chat_conversations c
        LEFT JOIN users u_seller ON c.seller_id = u_seller.id
        LEFT JOIN users u_buyer ON c.buyer_id = u_buyer.id
        WHERE c.buyer_id = %s OR c.seller_id = %s
        ORDER BY c.last_message_time DESC
    """
    
    conversations = db.execute(query, (user_id, user_id, user_id, user_id, user_id))
    
    return jsonify({
        'success': True,
        'conversations': conversations
    })

@chat_bp.route('/api/v1/chat/messages/<int:peer_id>', methods=['GET'])
@require_auth
def get_messages(peer_id):
    """Get messages with specific peer"""
    user_id = request.user_id
    is_seller = request.args.get('is_seller', 'true').lower() == 'true'
    
    # Get or create conversation
    if is_seller:
        conv_query = """
            SELECT id FROM chat_conversations
            WHERE buyer_id = %s AND seller_id = %s
        """
    else:
        conv_query = """
            SELECT id FROM chat_conversations
            WHERE buyer_id = %s AND seller_id = %s
        """
    
    conversation = db.execute_one(conv_query, (user_id, peer_id))
    
    if not conversation:
        return jsonify({'success': True, 'messages': []})
    
    # Get messages
    msg_query = """
        SELECT id, sender_id, recipient_id, content, is_read, created_at, read_at
        FROM chat_messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
    """
    
    messages = db.execute(msg_query, (conversation['id'],))
    
    # Mark messages as read
    mark_read_query = """
        UPDATE chat_messages
        SET is_read = TRUE, read_at = CURRENT_TIMESTAMP
        WHERE conversation_id = %s AND recipient_id = %s AND is_read = FALSE
    """
    db.execute(mark_read_query, (conversation['id'], user_id))
    
    return jsonify({
        'success': True,
        'messages': messages
    })

@chat_bp.route('/api/v1/chat/send', methods=['POST'])
@require_auth
def send_message():
    """Send a new message"""
    user_id = request.user_id
    data = request.get_json()
    
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_seller = data.get('is_seller', True)
    
    if not recipient_id or not content:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Get or create conversation
    if is_seller:
        conv_query = """
            INSERT INTO chat_conversations (buyer_id, seller_id)
            VALUES (%s, %s)
            ON CONFLICT (buyer_id, seller_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
    else:
        conv_query = """
            INSERT INTO chat_conversations (buyer_id, seller_id)
            VALUES (%s, %s)
            ON CONFLICT (buyer_id, seller_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
    
    conversation = db.execute_one(conv_query, (user_id, recipient_id))
    
    # Insert message
    msg_query = """
        INSERT INTO chat_messages (conversation_id, sender_id, recipient_id, content)
        VALUES (%s, %s, %s, %s)
        RETURNING id, created_at
    """
    
    message = db.execute_one(msg_query, (conversation['id'], user_id, recipient_id, content))
    
    return jsonify({
        'success': True,
        'message': message
    })

@chat_bp.route('/api/v1/chat/unread-count', methods=['GET'])
@require_auth
def get_unread_messages_count():
    """Get unread messages count"""
    user_id = request.user_id
    
    query = """
        SELECT COUNT(*) as count
        FROM chat_messages
        WHERE recipient_id = %s AND is_read = FALSE
    """
    
    result = db.execute_one(query, (user_id,))
    count = result['count'] if result else 0
    
    return jsonify({
        'success': True,
        'unread_count': count
    })

# Register blueprints in your main app
# app.register_blueprint(notifications_bp)
# app.register_blueprint(chat_bp)
