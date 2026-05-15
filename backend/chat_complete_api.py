# ============================================
# COMPLETE CHAT SYSTEM API
# Supports: Buyer-Seller, Buyer-Rider, Buyer-Admin, Seller-Admin, Rider-Admin
# ============================================

from flask import jsonify, request
from datetime import datetime
from sqlalchemy import or_, and_

# ============================================
# DATABASE MODELS (Add to your models if missing)
# ============================================

"""
# Add ChatMessage model to your database models:

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': {
                'id': self.sender.id,
                'name': f"{self.sender.first_name} {self.sender.last_name}",
                'role': self.sender.role,
                'profile_picture': self.sender.profile_picture
            },
            'receiver': {
                'id': self.receiver.id,
                'name': f"{self.receiver.first_name} {self.receiver.last_name}",
                'role': self.receiver.role,
                'profile_picture': self.receiver.profile_picture
            }
        }
"""

# ============================================
# CHAT API ENDPOINTS
# ============================================

@app.route('/api/chat/conversations', methods=['GET'])
@token_required
def api_get_conversations():
    """Get all conversations for current user"""
    try:
        user_id = request.current_user_id
        
        # Get all unique users the current user has chatted with
        sent_to = db.session.query(ChatMessage.receiver_id).filter(
            ChatMessage.sender_id == user_id
        ).distinct().all()
        
        received_from = db.session.query(ChatMessage.sender_id).filter(
            ChatMessage.receiver_id == user_id
        ).distinct().all()
        
        # Combine and get unique user IDs
        user_ids = set([u[0] for u in sent_to] + [u[0] for u in received_from])
        
        conversations = []
        for other_user_id in user_ids:
            other_user = db.session.get(User, other_user_id)
            if not other_user:
                continue
            
            # Get last message
            last_message = ChatMessage.query.filter(
                or_(
                    and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
                    and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id)
                )
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Count unread messages
            unread_count = ChatMessage.query.filter(
                ChatMessage.sender_id == other_user_id,
                ChatMessage.receiver_id == user_id,
                ChatMessage.is_read == False
            ).count()
            
            conversations.append({
                'user_id': other_user.id,
                'name': f"{other_user.first_name} {other_user.last_name}",
                'role': other_user.role,
                'profile_picture': other_user.profile_picture,
                'last_message': last_message.message if last_message else None,
                'last_message_time': last_message.created_at.isoformat() if last_message else None,
                'unread_count': unread_count,
                'is_online': False  # Can be enhanced with Socket.IO presence
            })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'conversations': conversations
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch conversations'
        }), 500


@app.route('/api/chat/messages/<int:other_user_id>', methods=['GET'])
@token_required
def api_get_messages(other_user_id):
    """Get all messages between current user and another user"""
    try:
        user_id = request.current_user_id
        
        # Verify other user exists
        other_user = db.session.get(User, other_user_id)
        if not other_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get messages
        messages = ChatMessage.query.filter(
            or_(
                and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
                and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id)
            )
        ).order_by(ChatMessage.created_at.asc()).all()
        
        # Mark messages as read
        unread_messages = ChatMessage.query.filter(
            ChatMessage.sender_id == other_user_id,
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False
        ).all()
        
        for msg in unread_messages:
            msg.is_read = True
        
        if unread_messages:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in messages],
            'other_user': {
                'id': other_user.id,
                'name': f"{other_user.first_name} {other_user.last_name}",
                'role': other_user.role,
                'profile_picture': other_user.profile_picture
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch messages'
        }), 500


@app.route('/api/chat/send', methods=['POST'])
@token_required
def api_send_message():
    """Send a message to another user"""
    try:
        user_id = request.current_user_id
        data = request.get_json()
        
        receiver_id = data.get('receiver_id')
        message = data.get('message', '').strip()
        
        if not receiver_id:
            return jsonify({
                'success': False,
                'error': 'Receiver ID is required'
            }), 400
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Verify receiver exists
        receiver = db.session.get(User, receiver_id)
        if not receiver:
            return jsonify({
                'success': False,
                'error': 'Receiver not found'
            }), 404
        
        # Create message
        chat_message = ChatMessage(
            sender_id=user_id,
            receiver_id=receiver_id,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        # Send real-time notification via Socket.IO
        try:
            sender = db.session.get(User, user_id)
            socketio.emit('new_message', {
                'message_id': chat_message.id,
                'sender_id': user_id,
                'sender_name': f"{sender.first_name} {sender.last_name}",
                'sender_role': sender.role,
                'sender_profile_picture': sender.profile_picture,
                'message': message,
                'created_at': chat_message.created_at.isoformat()
            }, room=f'user_{receiver_id}')
        except Exception as e:
            app.logger.error(f"Error sending Socket.IO notification: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': chat_message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500


@app.route('/api/chat/mark-read/<int:other_user_id>', methods=['POST'])
@token_required
def api_mark_messages_read(other_user_id):
    """Mark all messages from a user as read"""
    try:
        user_id = request.current_user_id
        
        messages = ChatMessage.query.filter(
            ChatMessage.sender_id == other_user_id,
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False
        ).all()
        
        for msg in messages:
            msg.is_read = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'marked_count': len(messages)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error marking messages as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark messages as read'
        }), 500


@app.route('/api/chat/unread-count', methods=['GET'])
@token_required
def api_get_unread_count():
    """Get total unread message count for current user"""
    try:
        user_id = request.current_user_id
        
        unread_count = ChatMessage.query.filter(
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False
        ).count()
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching unread count: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch unread count'
        }), 500


@app.route('/api/chat/search-users', methods=['GET'])
@token_required
def api_search_users():
    """Search for users to start a conversation"""
    try:
        user_id = request.current_user_id
        current_user = db.session.get(User, user_id)
        query = request.args.get('q', '').strip()
        role_filter = request.args.get('role', None)
        
        if not query and not role_filter:
            return jsonify({
                'success': True,
                'users': []
            }), 200
        
        # Build query
        search_query = User.query.filter(
            User.id != user_id,
            User.status == 'approved'
        )
        
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        if role_filter:
            search_query = search_query.filter(User.role == role_filter)
        
        users = search_query.limit(20).all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'role': user.role,
                'profile_picture': user.profile_picture
            })
        
        return jsonify({
            'success': True,
            'users': result
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error searching users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to search users'
        }), 500


# ============================================
# SOCKET.IO EVENTS FOR REAL-TIME CHAT
# ============================================

@socketio.on('join_chat')
def handle_join_chat():
    """User joins their personal chat room"""
    try:
        if hasattr(request, 'current_user_id'):
            user_id = request.current_user_id
            join_room(f'user_{user_id}')
            emit('joined_chat', {'message': 'Successfully joined chat'})
    except Exception as e:
        app.logger.error(f"Error joining chat: {str(e)}")


@socketio.on('typing')
def handle_typing(data):
    """Notify other user that current user is typing"""
    try:
        if hasattr(request, 'current_user_id'):
            receiver_id = data.get('receiver_id')
            if receiver_id:
                sender = db.session.get(User, request.current_user_id)
                socketio.emit('user_typing', {
                    'sender_id': request.current_user_id,
                    'sender_name': f"{sender.first_name} {sender.last_name}"
                }, room=f'user_{receiver_id}')
    except Exception as e:
        app.logger.error(f"Error handling typing event: {str(e)}")


@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Notify other user that current user stopped typing"""
    try:
        if hasattr(request, 'current_user_id'):
            receiver_id = data.get('receiver_id')
            if receiver_id:
                socketio.emit('user_stop_typing', {
                    'sender_id': request.current_user_id
                }, room=f'user_{receiver_id}')
    except Exception as e:
        app.logger.error(f"Error handling stop typing event: {str(e)}")


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_chat_partner_for_order(order_id, current_user_id):
    """Get the appropriate chat partner for an order"""
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return None
        
        current_user = db.session.get(User, current_user_id)
        if not current_user:
            return None
        
        # Determine chat partner based on user role
        if current_user.role == 'buyer':
            # Buyer can chat with seller or rider
            if order.rider_id:
                return order.rider_id
            elif order.items and order.items[0].product.seller_id:
                return order.items[0].product.seller_id
        elif current_user.role == 'seller':
            # Seller can chat with buyer
            return order.buyer_id
        elif current_user.role == 'rider':
            # Rider can chat with buyer
            return order.buyer_id
        
        return None
        
    except Exception as e:
        app.logger.error(f"Error getting chat partner: {str(e)}")
        return None


@app.route('/api/chat/order/<int:order_id>/partner', methods=['GET'])
@token_required
def api_get_order_chat_partner(order_id):
    """Get the chat partner for a specific order"""
    try:
        user_id = request.current_user_id
        partner_id = get_chat_partner_for_order(order_id, user_id)
        
        if not partner_id:
            return jsonify({
                'success': False,
                'error': 'No chat partner found for this order'
            }), 404
        
        partner = db.session.get(User, partner_id)
        if not partner:
            return jsonify({
                'success': False,
                'error': 'Chat partner not found'
            }), 404
        
        return jsonify({
            'success': True,
            'partner': {
                'id': partner.id,
                'name': f"{partner.first_name} {partner.last_name}",
                'role': partner.role,
                'profile_picture': partner.profile_picture
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting order chat partner: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get chat partner'
        }), 500
