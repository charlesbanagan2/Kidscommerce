# SELLER TO RIDER CHAT IMPLEMENTATION GUIDE

## Summary
Added chat functionality between sellers and riders for all orders. Sellers can now chat with assigned riders directly from the orders page and order detail page.

## Files Modified

### 1. backend/templates/seller/orders.html
- Added "Chat with Rider" button in the rider info section
- Button appears for all orders that have an assigned rider
- Links to: `/seller/chat/rider/<rider_id>/<order_id>`

### 2. backend/templates/seller/order_detail.html
- Added new "Assigned Rider" card showing rider information
- Includes rider name, phone number, and chat button
- Chat button links to: `/seller/chat/rider/<rider_id>/<order_id>`

### 3. backend/templates/seller/chat_rider.html (NEW FILE)
- Real-time chat interface for seller-to-rider communication
- Shows rider information in header
- Displays chat history
- Real-time messaging using Socket.IO
- Mobile-responsive design

## Backend Routes to Add (app.py)

Add these routes to your app.py file:

```python
@app.route('/seller/chat/rider/<int:rider_id>/<int:order_id>')
@login_required
@seller_required
def seller_chat_rider(rider_id, order_id):
    """Seller chat with rider for a specific order"""
    # Get rider information
    rider = db.session.get(User, rider_id)
    if not rider or rider.role != 'rider':
        flash('Rider not found.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Verify order exists and belongs to seller
    order = db.session.get(Order, order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Check if seller owns any items in this order
    seller_has_items = any(item.product.seller_id == session['user_id'] for item in order.items)
    if not seller_has_items:
        flash('You do not have access to this order.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Get chat messages between seller and rider for this order
    messages = RiderChatMessage.query.filter(
        or_(
            and_(
                RiderChatMessage.buyer_id == session['user_id'],  # Using buyer_id field for seller
                RiderChatMessage.rider_id == rider_id
            ),
            and_(
                RiderChatMessage.rider_id == rider_id,
                RiderChatMessage.buyer_id == session['user_id']
            )
        ),
        RiderChatMessage.order_id == order_id
    ).order_by(RiderChatMessage.created_at.asc()).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.rider_id == rider_id and msg.sender_role == 'rider' and not msg.is_read:
            msg.is_read = True
    db.session.commit()
    
    return render_template('seller/chat_rider.html',
                         rider=rider,
                         order_id=order_id,
                         messages=messages)


@app.route('/api/chat/send', methods=['POST'])
@login_required
def api_chat_send():
    """API endpoint to send chat message (seller to rider or buyer to rider)"""
    data = request.get_json()
    
    recipient_id = data.get('recipient_id')
    recipient_role = data.get('recipient_role')  # 'rider'
    message_text = data.get('message')
    order_id = data.get('order_id')
    
    if not all([recipient_id, recipient_role, message_text, order_id]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Determine sender role
    user = db.session.get(User, session['user_id'])
    sender_role = user.role if user.role in ['buyer', 'rider'] else 'seller'
    
    # Create message
    new_message = RiderChatMessage(
        buyer_id=session['user_id'],  # Using buyer_id for seller too (reusing field)
        rider_id=recipient_id,
        order_id=order_id,
        message=message_text,
        sender_role=sender_role,
        is_read=False
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    # Emit socket event
    try:
        socketio.emit('new_message', {
            'sender_id': session['user_id'],
            'sender_name': f"{user.first_name} {user.last_name}",
            'message': message_text,
            'created_at': new_message.created_at.isoformat()
        }, room=f'user_{recipient_id}')
    except:
        pass
    
    return jsonify({'success': True, 'message_id': new_message.id})
```

## Socket.IO Events

The chat uses these Socket.IO events (already handled by unified_chat_api.py):
- `join_chat`: Join a chat room
- `send_message`: Send a message
- `new_message`: Receive a message

## Database Schema

Uses existing `RiderChatMessage` table:
- `buyer_id`: Stores seller_id when seller is chatting (reusing field)
- `rider_id`: Rider user ID
- `order_id`: Associated order
- `message`: Message text
- `sender_role`: 'seller' or 'rider'
- `is_read`: Message read status
- `created_at`: Timestamp

## Features Implemented

✅ Chat button on seller orders page (for orders with assigned rider)
✅ Chat button on seller order detail page
✅ Real-time messaging using Socket.IO
✅ Message persistence in database
✅ Rider name and phone number display
✅ Mobile-responsive chat interface
✅ Message read status tracking
✅ Back navigation to order details

## Testing Checklist

1. ✅ Seller can see rider info (name + phone) on orders with assigned rider
2. ✅ Chat button appears on orders page
3. ✅ Chat button appears on order detail page
4. ⏳ Chat page loads with rider information
5. ⏳ Messages can be sent and received in real-time
6. ⏳ Chat history is persisted
7. ⏳ Back button returns to order detail page

## Next Steps

1. Add the two routes to app.py (seller_chat_rider and api_chat_send)
2. Test the chat functionality
3. Optionally: Add unread message badge count for sellers
4. Optionally: Add notification when rider sends message to seller
