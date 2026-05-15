"""
PRODUCT CHAT API
Allows buyers to message sellers about specific products
Similar to Shopee's product inquiry feature
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps

product_chat_bp = Blueprint('product_chat', __name__)

def register_product_chat_api(app, db, socketio, token_required):
    """Register product chat API with Flask app"""
    
    # ============================================
    # API ENDPOINTS
    # ============================================
    
    @app.route('/api/v1/chat/product/<int:product_id>/messages', methods=['GET'])
    @token_required
    def get_product_chat_messages(product_id):
        """Get all messages about a specific product"""
        try:
            from sqlalchemy import text
            
            user_id = request.current_user_id
            
            # Get product to find seller
            result = db.session.execute(
                text("SELECT seller_id FROM product WHERE id = :product_id"),
                {'product_id': product_id}
            )
            product_row = result.fetchone()
            if not product_row:
                return jsonify({'success': False, 'error': 'Product not found'}), 404
            
            seller_id = product_row[0]
            
            # Get messages
            if user_id == seller_id:
                # Seller: get all messages about this product
                messages_result = db.session.execute(text("""
                    SELECT id, sender_id, receiver_id, message, is_read, created_at
                    FROM chat_message
                    WHERE product_id = :product_id
                    AND (sender_id = :user_id OR receiver_id = :user_id)
                    ORDER BY created_at ASC
                """), {'product_id': product_id, 'user_id': user_id})
            else:
                # Buyer: get messages between buyer and seller
                messages_result = db.session.execute(text("""
                    SELECT id, sender_id, receiver_id, message, is_read, created_at
                    FROM chat_message
                    WHERE product_id = :product_id
                    AND ((sender_id = :user_id AND receiver_id = :seller_id)
                         OR (sender_id = :seller_id AND receiver_id = :user_id))
                    ORDER BY created_at ASC
                """), {'product_id': product_id, 'user_id': user_id, 'seller_id': seller_id})
            
            messages = messages_result.fetchall()
            
            # Mark as read
            db.session.execute(text("""
                UPDATE chat_message
                SET is_read = TRUE
                WHERE product_id = :product_id
                AND receiver_id = :user_id
                AND is_read = FALSE
            """), {'product_id': product_id, 'user_id': user_id})
            db.session.commit()
            
            # Format messages with sender info
            result = []
            for msg in messages:
                sender_result = db.session.execute(
                    text("SELECT id, first_name, last_name, role, profile_image FROM \"user\" WHERE id = :sender_id"),
                    {'sender_id': msg[1]}
                )
                sender_row = sender_result.fetchone()
                
                result.append({
                    'id': msg[0],
                    'sender_id': msg[1],
                    'receiver_id': msg[2],
                    'message': msg[3],
                    'is_read': msg[4],
                    'created_at': msg[5].isoformat() if msg[5] else None,
                    'sender': {
                        'id': sender_row[0],
                        'name': f"{sender_row[1]} {sender_row[2]}",
                        'role': sender_row[3],
                        'profile_picture': sender_row[4]
                    } if sender_row else None
                })
            
            # Get product info - use image_filename only
            product_result = db.session.execute(
                text("SELECT id, name, price, image_filename FROM product WHERE id = :product_id"),
                {'product_id': product_id}
            )
            product_row = product_result.fetchone()
            
            return jsonify({
                'success': True,
                'messages': result,
                'product': {
                    'id': product_row[0],
                    'name': product_row[1],
                    'price': float(product_row[2]) if product_row[2] else 0,
                    'image': product_row[3]
                } if product_row else None
            }), 200
            
        except Exception as e:
            print(f"[ERROR] get_product_chat_messages: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/v1/chat/product/send', methods=['POST'])
    @token_required
    def send_product_chat_message():
        """Send a message about a specific product"""
        try:
            from sqlalchemy import text
            from datetime import datetime
            
            data = request.get_json()
            product_id = data.get('product_id')
            receiver_id = data.get('receiver_id')
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            
            # Auto-fetch receiver_id from product if not provided
            if not receiver_id and product_id:
                result = db.session.execute(
                    text("SELECT seller_id FROM product WHERE id = :product_id"),
                    {'product_id': product_id}
                )
                product_row = result.fetchone()
                if product_row:
                    receiver_id = product_row[0]
            
            if not receiver_id:
                return jsonify({'success': False, 'error': 'Receiver not found'}), 400
            
            # Create message
            result = db.session.execute(text("""
                INSERT INTO chat_message (sender_id, receiver_id, message, product_id, is_read, created_at)
                VALUES (:sender_id, :receiver_id, :message, :product_id, FALSE, :created_at)
                RETURNING id, created_at
            """), {
                'sender_id': request.current_user_id,
                'receiver_id': receiver_id,
                'message': message,
                'product_id': product_id,
                'created_at': datetime.utcnow()
            })
            
            msg_row = result.fetchone()
            db.session.commit()
            
            # Send real-time notification
            try:
                sender_result = db.session.execute(
                    text("SELECT first_name, last_name FROM \"user\" WHERE id = :user_id"),
                    {'user_id': request.current_user_id}
                )
                sender_row = sender_result.fetchone()
                
                if sender_row:
                    product_result = db.session.execute(
                        text("SELECT name FROM product WHERE id = :product_id"),
                        {'product_id': product_id}
                    )
                    product_row = product_result.fetchone()
                    
                    socketio.emit('new_message', {
                        'message_id': msg_row[0],
                        'sender_id': request.current_user_id,
                        'sender_name': f"{sender_row[0]} {sender_row[1]}",
                        'message': message,
                        'product_id': product_id,
                        'product_name': product_row[0] if product_row else None,
                        'created_at': msg_row[1].isoformat()
                    }, room=f'user_{receiver_id}')
            except Exception as e:
                print(f"[WARNING] Socket.IO emit failed: {e}")
            
            return jsonify({
                'success': True,
                'message': {
                    'id': msg_row[0],
                    'sender_id': request.current_user_id,
                    'receiver_id': receiver_id,
                    'message': message,
                    'product_id': product_id,
                    'created_at': msg_row[1].isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] send_product_chat_message: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/v1/chat/conversations/product', methods=['GET'])
    @token_required
    def get_product_conversations():
        """Get all product-related conversations for current user"""
        try:
            from sqlalchemy import text
            
            user_id = request.current_user_id
            
            # Get distinct product_ids where user is involved
            product_ids_result = db.session.execute(text("""
                SELECT DISTINCT product_id
                FROM chat_message
                WHERE product_id IS NOT NULL
                AND (sender_id = :user_id OR receiver_id = :user_id)
            """), {'user_id': user_id})
            
            product_ids = [row[0] for row in product_ids_result.fetchall()]
            
            conversations = []
            for prod_id in product_ids:
                if not prod_id:
                    continue
                
                # Get product info - use image_filename only
                product_result = db.session.execute(
                    text("SELECT id, name, price, image_filename FROM product WHERE id = :prod_id"),
                    {'prod_id': prod_id}
                )
                product_row = product_result.fetchone()
                if not product_row:
                    continue
                
                # Get last message for this product
                last_msg_result = db.session.execute(text("""
                    SELECT id, sender_id, receiver_id, message, created_at
                    FROM chat_message
                    WHERE product_id = :prod_id
                    AND (sender_id = :user_id OR receiver_id = :user_id)
                    ORDER BY created_at DESC
                    LIMIT 1
                """), {'prod_id': prod_id, 'user_id': user_id})
                
                last_msg_row = last_msg_result.fetchone()
                if not last_msg_row:
                    continue
                
                # Determine other user
                other_user_id = last_msg_row[1] if last_msg_row[1] != user_id else last_msg_row[2]
                other_user_result = db.session.execute(
                    text("SELECT id, first_name, last_name, role, profile_image FROM \"user\" WHERE id = :other_user_id"),
                    {'other_user_id': other_user_id}
                )
                other_user_row = other_user_result.fetchone()
                
                # Count unread
                unread_result = db.session.execute(text("""
                    SELECT COUNT(*)
                    FROM chat_message
                    WHERE product_id = :prod_id
                    AND receiver_id = :user_id
                    AND is_read = FALSE
                """), {'prod_id': prod_id, 'user_id': user_id})
                unread = unread_result.scalar() or 0
                
                conversations.append({
                    'product_id': prod_id,
                    'product_name': product_row[1],
                    'product_image': product_row[3],
                    'product_price': float(product_row[2]) if product_row[2] else 0,
                    'other_user': {
                        'id': other_user_row[0],
                        'name': f"{other_user_row[1]} {other_user_row[2]}",
                        'role': other_user_row[3],
                        'profile_picture': other_user_row[4]
                    } if other_user_row else None,
                    'last_message': last_msg_row[3],
                    'last_message_time': last_msg_row[4].isoformat() if last_msg_row[4] else None,
                    'unread_count': unread
                })
            
            # Sort by last message time
            conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
            
            return jsonify({
                'success': True,
                'conversations': conversations
            }), 200
            
        except Exception as e:
            print(f"[ERROR] get_product_conversations: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("[OK] Product chat API registered")
    return product_chat_bp
