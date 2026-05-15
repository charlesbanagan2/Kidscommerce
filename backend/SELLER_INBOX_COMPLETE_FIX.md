===========================================
SELLER INBOX FIX - COMPLETE SOLUTION
===========================================

PROBLEMA:
- Buyer nag-sesend ng messages gamit ang chat_message table (unified chat)
- Seller inbox naghahanap sa StoreChatMessage table (old table)
- Kaya hindi nakikita ng seller ang messages

SOLUSYON:
1. I-update ang seller_inbox route para gumamit ng chat_message table
2. I-update ang seller_send_message route para mag-save sa chat_message table
3. Siguraduhin na may product info sa messages

===========================================
STEP 1: REPLACE SELLER INBOX ROUTE
===========================================

Sa app.py, line 12239, palitan ang buong seller_inbox function:

TANGGALIN ITO (OLD CODE):
```python
@app.route('/seller/inbox')
@login_required
def seller_inbox():
    seller_id = session['user_id']
    buyer_id = request.args.get('buyer_id', type=int)
    buyers = db.session.query(User).join(StoreChatMessage, User.id == StoreChatMessage.buyer_id)\
        .filter(StoreChatMessage.seller_id == seller_id)\
        .group_by(User.id).all()
    # ... rest of old code
```

PALITAN NG ITO (NEW CODE):
```python
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
```

===========================================
STEP 2: UPDATE SELLER SEND MESSAGE ROUTE
===========================================

Sa app.py, line 13103, palitan ang seller_send_message function:

TANGGALIN ITO (OLD CODE):
```python
@app.route('/seller/send-message/<int:buyer_id>', methods=['POST'])
# ... old code using StoreChatMessage
```

PALITAN NG ITO (NEW CODE):
```python
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
```

===========================================
STEP 3: VERIFY DATABASE TABLE
===========================================

Siguraduhin na may chat_message table sa database:

```sql
-- Check if table exists
SELECT * FROM chat_message LIMIT 1;

-- If table doesn't exist, create it:
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES "user"(id),
    receiver_id INTEGER NOT NULL REFERENCES "user"(id),
    message TEXT NOT NULL,
    product_id INTEGER REFERENCES product(id),
    order_id INTEGER REFERENCES "order"(id),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_message_sender ON chat_message(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_receiver ON chat_message(receiver_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_product ON chat_message(product_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_created ON chat_message(created_at DESC);
```

===========================================
STEP 4: TEST THE FIX
===========================================

1. Login as BUYER
2. Go to a product page
3. Click "Chat with Seller" or "Message Seller"
4. Send a message: "Hi! I'm interested in this product"
5. Logout

6. Login as SELLER
7. Go to /seller/inbox
8. You should see the buyer in the list
9. Click on the buyer
10. You should see the message
11. Reply to the buyer
12. Logout

13. Login as BUYER again
14. Check messages - you should see seller's reply

===========================================
DEBUGGING TIPS
===========================================

If messages still don't appear:

1. Check database:
```sql
SELECT * FROM chat_message ORDER BY created_at DESC LIMIT 10;
```

2. Check if messages are being saved:
```sql
SELECT 
    cm.id,
    cm.sender_id,
    cm.receiver_id,
    cm.message,
    cm.created_at,
    u1.first_name || ' ' || u1.last_name as sender_name,
    u2.first_name || ' ' || u2.last_name as receiver_name
FROM chat_message cm
JOIN "user" u1 ON cm.sender_id = u1.id
JOIN "user" u2 ON cm.receiver_id = u2.id
ORDER BY cm.created_at DESC
LIMIT 10;
```

3. Check server logs for errors:
```
[ERROR] seller_inbox: ...
[ERROR] seller_send_message: ...
```

4. Check browser console for JavaScript errors

5. Verify Socket.IO connection:
```javascript
// In browser console
socket.connected  // should be true
```

===========================================
SUMMARY OF CHANGES
===========================================

✅ Updated seller_inbox route to use chat_message table
✅ Updated seller_send_message route to save to chat_message table
✅ Added product info display in messages
✅ Added real-time Socket.IO notifications
✅ Maintained backward compatibility with existing inbox.html template
✅ Added proper error handling and logging

RESULT:
- Buyer messages will now appear in seller inbox
- Seller can reply and buyer will receive the messages
- Product info is displayed when chatting about a product
- Real-time updates via Socket.IO
