"""
Notification and Chat API for Mobile App
Handles buyer notifications and chat messages with database persistence
"""
from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ykgwqdboucsiaedgtivx.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

notification_chat_bp = Blueprint('notification_chat', __name__)

# JWT Secret - Will be loaded from environment when needed
_JWT_SECRET = None

def get_jwt_secret():
    """Get JWT_SECRET_KEY from environment (lazy loading)"""
    global _JWT_SECRET
    if _JWT_SECRET is None:
        _JWT_SECRET = os.getenv('JWT_SECRET_KEY')  # Use JWT_SECRET_KEY for consistency
        if not _JWT_SECRET:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is not set! "
                "Please add JWT_SECRET_KEY to your .env file."
            )
    return _JWT_SECRET

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
            current_user_id = data.get('user_id')
        except Exception as e:
            return jsonify({'success': False, 'message': f'Invalid token: {str(e)}'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated


# ============= NOTIFICATION ENDPOINTS =============

@notification_chat_bp.route('/api/v1/notifications', methods=['GET'])
@token_required
def get_notifications(current_user_id):
    """Get all notifications for current user"""
    try:
        # Get notifications from database
        response = supabase.table('notification')\
            .select('*')\
            .eq('user_id', current_user_id)\
            .order('created_at', desc=True)\
            .limit(100)\
            .execute()
        
        notifications = response.data if response.data else []
        
        # Count unread
        unread_count = sum(1 for n in notifications if not n.get('is_read', False))
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to fetch notifications: {str(e)}'
        }), 500


@notification_chat_bp.route('/api/v1/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count(current_user_id):
    """Get count of unread notifications"""
    try:
        response = supabase.table('notification')\
            .select('id', count='exact')\
            .eq('user_id', current_user_id)\
            .eq('is_read', False)\
            .execute()
        
        count = response.count if hasattr(response, 'count') else 0
        
        return jsonify({
            'success': True,
            'unread_count': count
        }), 200
        
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return jsonify({
            'success': False,
            'unread_count': 0
        }), 200


@notification_chat_bp.route('/api/v1/notifications/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(current_user_id, notification_id):
    """Mark a notification as read"""
    try:
        response = supabase.table('notification')\
            .update({'is_read': True})\
            .eq('id', notification_id)\
            .eq('user_id', current_user_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        }), 200
        
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to mark as read: {str(e)}'
        }), 500


@notification_chat_bp.route('/api/v1/notifications/mark-all-read', methods=['PUT'])
@token_required
def mark_all_read(current_user_id):
    """Mark all notifications as read"""
    try:
        response = supabase.table('notification')\
            .update({'is_read': True})\
            .eq('user_id', current_user_id)\
            .eq('is_read', False)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        }), 200
        
    except Exception as e:
        print(f"Error marking all as read: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to mark all as read: {str(e)}'
        }), 500


# ============= CHAT ENDPOINTS =============

@notification_chat_bp.route('/api/v1/chat/conversations', methods=['GET'])
@token_required
def get_conversations(current_user_id):
    """Get all chat conversations for current user"""
    try:
        # Get conversations from store_chat_message table
        # Group by seller/rider and get latest message
        response = supabase.rpc('get_buyer_conversations', {
            'buyer_id_param': current_user_id
        }).execute()
        
        # If RPC doesn't exist, fallback to manual query
        if not response.data:
            # Get all messages where user is buyer
            messages_response = supabase.table('store_chat_message')\
                .select('*, seller:seller_id(id, first_name, last_name, profile_image)')\
                .eq('buyer_id', current_user_id)\
                .order('created_at', desc=True)\
                .execute()
            
            # Group by seller
            conversations = {}
            for msg in messages_response.data if messages_response.data else []:
                seller_id = msg.get('seller_id')
                if seller_id not in conversations:
                    seller = msg.get('seller', {})
                    conversations[seller_id] = {
                        'peer_id': seller_id,
                        'peer_name': f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() or 'Seller',
                        'peer_avatar': seller.get('profile_image'),
                        'last_message': msg.get('message', ''),
                        'last_message_time': msg.get('created_at'),
                        'unread_count': 0,
                        'is_peer_seller': True
                    }
            
            conversations_list = list(conversations.values())
        else:
            conversations_list = response.data
        
        return jsonify({
            'success': True,
            'conversations': conversations_list
        }), 200
        
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return jsonify({
            'success': False,
            'conversations': [],
            'message': f'Failed to fetch conversations: {str(e)}'
        }), 200


@notification_chat_bp.route('/api/v1/chat/messages/<int:peer_id>', methods=['GET'])
@token_required
def get_chat_messages(current_user_id, peer_id):
    """Get chat messages with a specific seller/rider"""
    try:
        is_seller = request.args.get('is_seller', 'true').lower() == 'true'
        
        if is_seller:
            # Get messages from store_chat_message
            response = supabase.table('store_chat_message')\
                .select('*')\
                .or_(f'and(buyer_id.eq.{current_user_id},seller_id.eq.{peer_id}),and(buyer_id.eq.{peer_id},seller_id.eq.{current_user_id})')\
                .order('created_at', desc=False)\
                .execute()
        else:
            # Get messages from rider_chat_message
            response = supabase.table('rider_chat_message')\
                .select('*')\
                .or_(f'and(buyer_id.eq.{current_user_id},rider_id.eq.{peer_id}),and(buyer_id.eq.{peer_id},rider_id.eq.{current_user_id})')\
                .order('created_at', desc=False)\
                .execute()
        
        messages = response.data if response.data else []
        
        # Mark messages as read
        if is_seller:
            supabase.table('store_chat_message')\
                .update({'is_read': True})\
                .eq('buyer_id', current_user_id)\
                .eq('seller_id', peer_id)\
                .eq('is_read', False)\
                .execute()
        else:
            supabase.table('rider_chat_message')\
                .update({'is_read': True})\
                .eq('buyer_id', current_user_id)\
                .eq('rider_id', peer_id)\
                .eq('is_read', False)\
                .execute()
        
        return jsonify({
            'success': True,
            'messages': messages
        }), 200
        
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({
            'success': False,
            'messages': [],
            'message': f'Failed to fetch messages: {str(e)}'
        }), 200


@notification_chat_bp.route('/api/v1/chat/send', methods=['POST'])
@token_required
def send_message(current_user_id):
    """Send a chat message"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()
        is_seller = data.get('is_seller', True)
        
        if not recipient_id or not content:
            return jsonify({
                'success': False,
                'message': 'Recipient ID and content are required'
            }), 400
        
        message_data = {
            'message': content,
            'sender_role': 'buyer',
            'is_read': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if is_seller:
            message_data['buyer_id'] = current_user_id
            message_data['seller_id'] = recipient_id
            table = 'store_chat_message'
        else:
            message_data['buyer_id'] = current_user_id
            message_data['rider_id'] = recipient_id
            table = 'rider_chat_message'
        
        response = supabase.table(table).insert(message_data).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'message': 'Message sent',
                'data': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send message'
            }), 500
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to send message: {str(e)}'
        }), 500


@notification_chat_bp.route('/api/v1/chat/unread-count', methods=['GET'])
@token_required
def get_unread_messages_count(current_user_id):
    """Get count of unread messages"""
    try:
        # Count unread from store_chat_message
        seller_response = supabase.table('store_chat_message')\
            .select('id', count='exact')\
            .eq('buyer_id', current_user_id)\
            .eq('is_read', False)\
            .execute()
        
        # Count unread from rider_chat_message
        rider_response = supabase.table('rider_chat_message')\
            .select('id', count='exact')\
            .eq('buyer_id', current_user_id)\
            .eq('is_read', False)\
            .execute()
        
        seller_count = seller_response.count if hasattr(seller_response, 'count') else 0
        rider_count = rider_response.count if hasattr(rider_response, 'count') else 0
        
        total_count = seller_count + rider_count
        
        return jsonify({
            'success': True,
            'unread_count': total_count,
            'seller_unread': seller_count,
            'rider_unread': rider_count
        }), 200
        
    except Exception as e:
        print(f"Error getting unread messages count: {e}")
        return jsonify({
            'success': False,
            'unread_count': 0
        }), 200


# Helper function to create notification
def create_notification(user_id, title, message, notification_type='info', order_id=None):
    """Helper to create a notification"""
    try:
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'is_read': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if order_id:
            notification_data['order_id'] = order_id
        
        supabase.table('notification').insert(notification_data).execute()
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        return False
