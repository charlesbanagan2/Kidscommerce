"""
UNIFIED CHAT SYSTEM API
Supports all user-to-user chat combinations:
- Buyer ↔ Seller
- Buyer ↔ Rider  
- Seller ↔ Rider
- Any user ↔ Any user

Uses a single ChatMessage table for all conversations.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room
from datetime import datetime
from sqlalchemy import or_, and_, func
from functools import wraps

def register_unified_chat_api(app, socketio, db, get_avatar_url=None, **_kwargs):
    """Register unified chat system with Flask app.

    get_avatar_url: optional callable(user_id, user_role) -> str for profile photo URLs.
    """
    if get_avatar_url is None and _kwargs.get('get_avatar_url'):
        get_avatar_url = _kwargs['get_avatar_url']
    
    # Create blueprint FIRST before defining routes
    chat_bp = Blueprint('unified_chat', __name__)
    
    # ============================================
    # DATABASE MODEL
    # ============================================
    
    class ChatMessage(db.Model):
        __tablename__ = 'chat_message'
        
        id = db.Column(db.Integer, primary_key=True)
        sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        message = db.Column(db.Text, nullable=False)
        product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)  # For product chats
        order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)  # For order chats
        is_read = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Table will be created by setup_chat_database.py
    # This just defines the model
    print("[OK] ChatMessage model loaded")
    
    # ============================================
    # HELPER FUNCTIONS
    # ============================================
    
    def get_user_from_token():
        """Extract user_id from JWT token in request"""
        if hasattr(request, 'current_user_id'):
            return request.current_user_id
        
        # Try to extract from Authorization header
        import jwt
        import os
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-mobile-jwt-secret-key-change-in-production')
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                return payload.get('user_id')
            except:
                pass
        return None
    
    # ============================================
    # API ENDPOINTS
    # ============================================
    
    @chat_bp.route('/api/chat/conversations', methods=['GET'])
    @chat_bp.route('/api/v1/chat/conversations', methods=['GET'])
    def get_conversations():
        """Get all conversations for current user"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            # Get unique users current user has chatted with
            subq_sent = db.session.query(ChatMessage.receiver_id).filter(
                ChatMessage.sender_id == user_id
            ).distinct()
            
            subq_received = db.session.query(ChatMessage.sender_id).filter(
                ChatMessage.receiver_id == user_id
            ).distinct()
            
            # Combine both
            peer_ids = set()
            for row in subq_sent.all():
                peer_ids.add(row[0])
            for row in subq_received.all():
                peer_ids.add(row[0])
            
            conversations = []
            for peer_id in peer_ids:
                # Get peer user info and seller store logo if applicable
                from sqlalchemy import text
                result = db.session.execute(
                    text("""
                        SELECT u.id, u.first_name, u.last_name, u.role, u.profile_picture,
                               sa.store_logo, sa.store_name
                        FROM "user" u
                        LEFT JOIN seller_application sa ON u.id = sa.user_id AND sa.status = 'approved'
                        WHERE u.id = :peer_id
                    """),
                    {'peer_id': peer_id}
                )
                peer_row = result.fetchone()
                if not peer_row:
                    continue
                
                if peer_row[3] == 'seller' and peer_row[5]:
                    profile_pic = peer_row[5]
                elif get_avatar_url:
                    profile_pic = get_avatar_url(peer_row[0], peer_row[3])
                else:
                    profile_pic = peer_row[4]
                display_name = peer_row[6] if peer_row[6] else f"{peer_row[1]} {peer_row[2]}"  # store_name or full name
                
                # Get last message
                last_msg = ChatMessage.query.filter(
                    or_(
                        and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == peer_id),
                        and_(ChatMessage.sender_id == peer_id, ChatMessage.receiver_id == user_id)
                    )
                ).order_by(ChatMessage.created_at.desc()).first()
                
                # Count unread
                unread = ChatMessage.query.filter(
                    ChatMessage.sender_id == peer_id,
                    ChatMessage.receiver_id == user_id,
                    ChatMessage.is_read == False
                ).count()
                
                conversations.append({
                    'peer_id': peer_row[0],
                    'peer_name': display_name,
                    'peer_role': peer_row[3],
                    'peer_profile_picture': profile_pic,
                    'last_message': last_msg.message if last_msg else None,
                    'last_message_time': last_msg.created_at.isoformat() if last_msg else None,
                    'unread_count': unread
                })
            
            # Sort by last message time
            conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
            
            return jsonify({
                'success': True,
                'conversations': conversations
            }), 200
            
        except Exception as e:
            print(f"[ERROR] Error fetching conversations: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @chat_bp.route('/api/chat/messages/<int:other_user_id>', methods=['GET'])
    @chat_bp.route('/api/v1/chat/messages/<int:other_user_id>', methods=['GET'])
    def get_messages(other_user_id):
        """Get all messages with a specific user"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            # Get messages
            messages = ChatMessage.query.filter(
                or_(
                    and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
                    and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id)
                )
            ).order_by(ChatMessage.created_at.asc()).all()
            
            # Mark as read
            unread = ChatMessage.query.filter(
                ChatMessage.sender_id == other_user_id,
                ChatMessage.receiver_id == user_id,
                ChatMessage.is_read == False
            ).all()
            
            for msg in unread:
                msg.is_read = True
            
            if unread:
                db.session.commit()
            
            # Get sender info for all messages using raw SQL
            from sqlalchemy import text
            sender_cache = {}
            
            # Format messages
            result = []
            for msg in messages:
                # Get sender info from cache or database with store logo
                if msg.sender_id not in sender_cache:
                    sender_result = db.session.execute(
                        text("""
                            SELECT u.id, u.first_name, u.last_name, u.role, u.profile_picture,
                                   sa.store_logo, sa.store_name
                            FROM "user" u
                            LEFT JOIN seller_application sa ON u.id = sa.user_id AND sa.status = 'approved'
                            WHERE u.id = :sender_id
                        """),
                        {'sender_id': msg.sender_id}
                    )
                    sender_row = sender_result.fetchone()
                    if sender_row:
                        if sender_row[3] == 'seller' and sender_row[5]:
                            profile_pic = sender_row[5]
                        elif get_avatar_url:
                            profile_pic = get_avatar_url(sender_row[0], sender_row[3])
                        else:
                            profile_pic = sender_row[4]
                        display_name = sender_row[6] if sender_row[6] else f"{sender_row[1]} {sender_row[2]}"
                        sender_cache[msg.sender_id] = {
                            'id': sender_row[0],
                            'name': display_name,
                            'role': sender_row[3],
                            'profile_picture': profile_pic
                        }
                
                sender_info = sender_cache.get(msg.sender_id, {
                    'id': msg.sender_id,
                    'name': 'Unknown',
                    'role': 'unknown',
                    'profile_picture': None
                })
                
                result.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'receiver_id': msg.receiver_id,
                    'message': msg.message,
                    'is_read': msg.is_read,
                    'created_at': msg.created_at.isoformat(),
                    'sender': sender_info
                })
            
            return jsonify({
                'success': True,
                'messages': result
            }), 200
            
        except Exception as e:
            print(f"[ERROR] Error fetching messages: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @chat_bp.route('/api/chat/send', methods=['POST'])
    @chat_bp.route('/api/v1/chat/send', methods=['POST'])
    def send_message():
        """Send a message to another user"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            receiver_id = data.get('receiver_id')
            message = data.get('message', '').strip()
            
            if not receiver_id or not message:
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Create message
            chat_msg = ChatMessage(
                sender_id=user_id,
                receiver_id=receiver_id,
                message=message,
                is_read=False
            )
            
            db.session.add(chat_msg)
            db.session.commit()
            
            # Send real-time notification via Socket.IO
            try:
                from sqlalchemy import text
                result = db.session.execute(
                    text("SELECT first_name, last_name, role FROM \"user\" WHERE id = :user_id"),
                    {'user_id': user_id}
                )
                sender_row = result.fetchone()
                if sender_row:
                    socketio.emit('new_message', {
                        'message_id': chat_msg.id,
                        'sender_id': user_id,
                        'sender_name': f"{sender_row[0]} {sender_row[1]}",
                        'sender_role': sender_row[2],
                        'message': message,
                        'created_at': chat_msg.created_at.isoformat()
                    }, room=f'user_{receiver_id}')
            except Exception as e:
                print(f"[WARNING] Socket.IO emit failed: {e}")
            
            return jsonify({
                'success': True,
                'message': {
                    'id': chat_msg.id,
                    'sender_id': user_id,
                    'receiver_id': receiver_id,
                    'message': message,
                    'created_at': chat_msg.created_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error sending message: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @chat_bp.route('/api/chat/unread-count', methods=['GET'])
    def get_unread_count():
        """Get total unread message count"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            count = ChatMessage.query.filter(
                ChatMessage.receiver_id == user_id,
                ChatMessage.is_read == False
            ).count()
            
            return jsonify({
                'success': True,
                'unread_count': count
            }), 200
            
        except Exception as e:
            print(f"[ERROR] Error getting unread count: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Mobile app endpoints with /api/v1 prefix
    @chat_bp.route('/api/v1/chat/unread-count', methods=['GET'])
    def get_unread_count_v1():
        """Get total unread message count (mobile v1)"""
        return get_unread_count()
    
    @chat_bp.route('/api/v1/chat/product/start', methods=['POST'])
    def start_product_chat():
        """Start a chat about a product"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            product_id = data.get('product_id')
            seller_id = data.get('seller_id')
            initial_message = data.get('message', '').strip()
            
            if not product_id:
                return jsonify({'success': False, 'error': 'Missing product_id'}), 400
            
            # Get product to find seller if not provided
            if not seller_id:
                from sqlalchemy import text
                result = db.session.execute(
                    text("SELECT seller_id FROM product WHERE id = :product_id"),
                    {'product_id': product_id}
                )
                product_row = result.fetchone()
                if not product_row:
                    return jsonify({'success': False, 'error': 'Product not found'}), 404
                seller_id = product_row[0]
            
            if not seller_id:
                return jsonify({'success': False, 'error': 'Seller not found'}), 404
            
            # Create initial message if provided
            if initial_message:
                chat_msg = ChatMessage(
                    sender_id=user_id,
                    receiver_id=seller_id,
                    message=initial_message,
                    product_id=product_id,
                    is_read=False
                )
                db.session.add(chat_msg)
                db.session.commit()
                
                # Send real-time notification
                try:
                    from sqlalchemy import text
                    result = db.session.execute(
                        text("SELECT first_name, last_name FROM \"user\" WHERE id = :user_id"),
                        {'user_id': user_id}
                    )
                    sender_row = result.fetchone()
                    if sender_row:
                        socketio.emit('new_message', {
                            'message_id': chat_msg.id,
                            'sender_id': user_id,
                            'sender_name': f"{sender_row[0]} {sender_row[1]}",
                            'message': initial_message,
                            'product_id': product_id,
                            'created_at': chat_msg.created_at.isoformat()
                        }, room=f'user_{seller_id}')
                except Exception as e:
                    print(f"[WARNING] Socket.IO emit failed: {e}")
            
            return jsonify({
                'success': True,
                'conversation': {
                    'peer_id': seller_id,
                    'product_id': product_id
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] start_product_chat: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ============================================
    # SOCKET.IO EVENTS
    # ============================================
    
    @socketio.on('join_chat')
    def handle_join_chat(data=None):
        """User joins their personal chat room"""
        try:
            user_id = get_user_from_token()
            if user_id:
                join_room(f'user_{user_id}')
                emit('joined_chat', {'message': 'Connected to chat'})
        except Exception as e:
            print(f"[ERROR] Error joining chat: {e}")
    
    @socketio.on('typing')
    def handle_typing(data):
        """Notify other user that current user is typing"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return
            
            receiver_id = data.get('receiver_id')
            if receiver_id:
                socketio.emit('user_typing', {
                    'sender_id': user_id
                }, room=f'user_{receiver_id}')
        except Exception as e:
            print(f"[ERROR] Error handling typing: {e}")
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """Notify other user that current user stopped typing"""
        try:
            user_id = get_user_from_token()
            if not user_id:
                return
            
            receiver_id = data.get('receiver_id')
            if receiver_id:
                socketio.emit('user_stop_typing', {
                    'sender_id': user_id
                }, room=f'user_{receiver_id}')
        except Exception as e:
            print(f"[ERROR] Error handling stop typing: {e}")
    
    # Register blueprint
    app.register_blueprint(chat_bp)
    
    print("[OK] Unified chat system registered")
    return chat_bp
