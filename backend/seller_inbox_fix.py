# SELLER INBOX FIX - Replace existing route at line 12239

# OLD CODE (REMOVE):
# @app.route('/seller/inbox')
# @login_required
# def seller_inbox():
#     seller_id = session['user_id']
#     buyer_id = request.args.get('buyer_id', type=int)
#     buyers = db.session.query(User).join(StoreChatMessage, User.id == StoreChatMessage.buyer_id)\
#         .filter(StoreChatMessage.seller_id == seller_id)\
#         .group_by(User.id).all()
#     ...

# NEW CODE (REPLACE WITH):

@app.route('/seller/inbox')
@login_required
def seller_inbox():
    """Seller inbox - view all buyer messages using unified chat_message table"""
    try:
        seller_id = session['user_id']
        buyer_id = request.args.get('buyer_id', type=int)
        
        from sqlalchemy import text
        
        # Get all unique buyers who messaged this seller
        buyers_result = db.session.execute(text("""
            SELECT DISTINCT 
                u.id, 
                u.first_name, 
                u.last_name, 
                u.profile_picture,
                (SELECT COUNT(*) FROM chat_message 
                 WHERE sender_id = u.id 
                 AND receiver_id = :seller_id 
                 AND is_read = FALSE) as unread_count,
                (SELECT message FROM chat_message 
                 WHERE (sender_id = u.id AND receiver_id = :seller_id)
                    OR (sender_id = :seller_id AND receiver_id = u.id)
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                (SELECT created_at FROM chat_message 
                 WHERE (sender_id = u.id AND receiver_id = :seller_id)
                    OR (sender_id = :seller_id AND receiver_id = u.id)
                 ORDER BY created_at DESC LIMIT 1) as last_message_time
            FROM "user" u
            WHERE EXISTS (
                SELECT 1 FROM chat_message cm
                WHERE (cm.sender_id = u.id AND cm.receiver_id = :seller_id)
                   OR (cm.sender_id = :seller_id AND cm.receiver_id = u.id)
            )
            ORDER BY last_message_time DESC
        """), {'seller_id': seller_id})
        
        buyers = []
        for row in buyers_result:
            buyer_obj = type('obj', (object,), {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'profile_picture': row[3] or '/static/user_avatar.png',
                'unread_count': row[4] or 0,
                'last_message': type('obj', (object,), {
                    'message': row[5],
                    'created_at': row[6]
                })() if row[5] else None
            })()
            buyers.append(buyer_obj)
        
        # Get chat thread if buyer selected
        chat_thread = []
        if buyer_id:
            # Mark messages as read
            db.session.execute(text("""
                UPDATE chat_message
                SET is_read = TRUE
                WHERE sender_id = :buyer_id
                AND receiver_id = :seller_id
                AND is_read = FALSE
            """), {'buyer_id': buyer_id, 'seller_id': seller_id})
            db.session.commit()
            
            # Get messages
            messages_result = db.session.execute(text("""
                SELECT 
                    cm.id,
                    cm.sender_id,
                    cm.receiver_id,
                    cm.message,
                    cm.product_id,
                    cm.is_read,
                    cm.created_at,
                    u.first_name,
                    u.last_name,
                    u.profile_picture,
                    p.id as prod_id,
                    p.name as prod_name,
                    p.price as prod_price,
                    p.image_filename as prod_image
                FROM chat_message cm
                JOIN "user" u ON cm.sender_id = u.id
                LEFT JOIN product p ON cm.product_id = p.id
                WHERE (cm.sender_id = :seller_id AND cm.receiver_id = :buyer_id)
                   OR (cm.sender_id = :buyer_id AND cm.receiver_id = :seller_id)
                ORDER BY cm.created_at ASC
            """), {'seller_id': seller_id, 'buyer_id': buyer_id})
            
            for row in messages_result:
                msg_obj = type('obj', (object,), {
                    'id': row[0],
                    'sender_id': row[1],
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'message': row[3],
                    'product_id': row[4],
                    'is_read': row[5],
                    'created_at': row[6],
                    'sender_role': 'seller' if row[1] == seller_id else 'buyer',
                    'buyer': type('obj', (object,), {
                        'first_name': row[7] if row[1] == buyer_id else '',
                        'last_name': row[8] if row[1] == buyer_id else '',
                        'profile_picture': row[9] if row[1] == buyer_id else '/static/user_avatar.png'
                    })(),
                    'seller': type('obj', (object,), {
                        'first_name': row[7] if row[1] == seller_id else '',
                        'last_name': row[8] if row[1] == seller_id else ''
                    })(),
                    'product': type('obj', (object,), {
                        'id': row[10],
                        'name': row[11],
                        'price': float(row[12]) if row[12] else 0,
                        'image_filename': row[13]
                    })() if row[10] else None
                })()
                chat_thread.append(msg_obj)
        
        # Get seller's products for quick product sharing
        products = Product.query.filter_by(seller_id=seller_id, status='active').all()
        
        quick_replies = [
            "Hello! How can I help you today?",
            "This product is available.",
            "Shipping is usually 1-3 days.",
            "Thank you for your order!"
        ]
        
        return render_template(
            'seller/inbox.html',
            buyers=buyers,
            chat_thread=chat_thread,
            products=products,
            quick_replies=quick_replies,
            selected_buyer_id=buyer_id
        )
        
    except Exception as e:
        print(f"[ERROR] seller_inbox: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading inbox', 'error')
        return redirect(url_for('seller_dashboard'))


# ADD NEW API ENDPOINT FOR SENDING MESSAGES
@app.route('/seller/send-message/<int:buyer_id>', methods=['POST'])
@login_required
def seller_send_message(buyer_id):
    """Send message from seller to buyer"""
    try:
        seller_id = session['user_id']
        
        # Get message from form or JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '').strip()
            product_id = data.get('product_id')
        else:
            message = request.form.get('message', '').strip()
            product_id = request.form.get('product_id')
        
        if not message:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            flash('Message is required', 'error')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))
        
        from sqlalchemy import text
        
        # Insert message into chat_message table
        result = db.session.execute(text("""
            INSERT INTO chat_message (sender_id, receiver_id, message, product_id, is_read, created_at)
            VALUES (:sender_id, :receiver_id, :message, :product_id, FALSE, :created_at)
            RETURNING id, created_at
        """), {
            'sender_id': seller_id,
            'receiver_id': buyer_id,
            'message': message,
            'product_id': product_id if product_id else None,
            'created_at': datetime.utcnow()
        })
        
        msg_row = result.fetchone()
        db.session.commit()
        
        # Send real-time notification via Socket.IO
        try:
            seller_result = db.session.execute(text("""
                SELECT first_name, last_name FROM "user" WHERE id = :seller_id
            """), {'seller_id': seller_id})
            seller_row = seller_result.fetchone()
            
            if seller_row:
                socketio.emit('new_message', {
                    'message_id': msg_row[0],
                    'sender_id': seller_id,
                    'sender_name': f"{seller_row[0]} {seller_row[1]}",
                    'sender_role': 'seller',
                    'message': message,
                    'product_id': product_id,
                    'created_at': msg_row[1].isoformat()
                }, room=f'user_{buyer_id}')
        except Exception as e:
            print(f"[WARNING] Socket.IO emit failed: {e}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': {
                    'id': msg_row[0],
                    'sender_id': seller_id,
                    'receiver_id': buyer_id,
                    'message': message,
                    'created_at': msg_row[1].isoformat()
                }
            })
        else:
            flash('Message sent successfully', 'success')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] seller_send_message: {e}")
        import traceback
        traceback.print_exc()
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Error sending message', 'error')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))
