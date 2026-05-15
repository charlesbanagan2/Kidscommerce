# Seller to Rider Chat Fix - Complete Solution

## Problem Identified
The `seller_chat_rider` route in `app.py` (around line 12263) is using the OLD `RiderChatMessage` table instead of the UNIFIED `chat_message` table. This causes:

1. ✗ Messages sent by seller don't appear in rider's inbox
2. ✗ Rider can't see seller's messages  
3. ✗ Chat conversations are not synced between seller and rider
4. ✗ The unified chat API is already registered but not being used

## Root Cause
The route is querying `RiderChatMessage` table which is separate from the unified `chat_message` table used by the chat API.

## Solution
The seller-to-rider chat should use the unified chat API endpoints instead of the old RiderChatMessage model.

### Option 1: Update Backend Route (Recommended)
Replace the `seller_chat_rider` function in `app.py` to use the unified chat_message table:

```python
@app.route('/seller/chat/rider/<int:rider_id>', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_chat_rider(rider_id):
    """Seller chat with rider about an order using UNIFIED chat system"""
    seller_id = session['user_id']
    order_id = request.args.get('order_id', type=int)
    
    rider = User.query.get_or_404(rider_id)
    
    # Use UNIFIED ChatMessage table (from unified_chat_api.py)
    from sqlalchemy import or_, and_
    
    # Import the ChatMessage model from unified_chat_api
    # Since it's registered in the blueprint, we need to access it via db.Model
    ChatMessage = db.Model.metadata.tables.get('chat_message')
    if ChatMessage is None:
        # Fallback: define inline if not found
        class ChatMessage(db.Model):
            __tablename__ = 'chat_message'
            id = db.Column(db.Integer, primary_key=True)
            sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            message = db.Column(db.Text, nullable=False)
            product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
            order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
            is_read = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Get chat messages between seller and rider using UNIFIED table
    chat_messages = db.session.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.sender_id == seller_id, ChatMessage.receiver_id == rider_id),
            and_(ChatMessage.sender_id == rider_id, ChatMessage.receiver_id == seller_id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Mark messages from rider as read
    db.session.query(ChatMessage).filter(
        ChatMessage.sender_id == rider_id,
        ChatMessage.receiver_id == seller_id,
        ChatMessage.is_read == False
    ).update({ChatMessage.is_read: True})
    db.session.commit()
    
    # Handle POST (send message)
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            # Create message in UNIFIED chat_message table
            chat = ChatMessage(
                sender_id=seller_id,
                receiver_id=rider_id,
                message=message,
                order_id=order_id,
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(chat)
            db.session.commit()
            
            # Send notification to rider
            try:
                seller_user = db.session.get(User, seller_id)
                push_notification(
                    rider_id,
                    f"Seller {seller_user.first_name} sent you a message.",
                    link=url_for('rider_chat_conversations'),
                    actor_user_id=seller_id,
                    type='chat'
                )
                # Emit to rider's room
                socketio.emit('new_message', {
                    'sender_id': seller_id,
                    'sender_name': f"{seller_user.first_name} {seller_user.last_name}",
                    'message': message,
                    'created_at': chat.created_at.isoformat()
                }, room=f'user_{rider_id}')
            except Exception as e:
                print(f"Error sending notification: {e}")
            
            return redirect(url_for('seller_chat_rider', rider_id=rider_id, order_id=order_id))
    
    rider_profile = DeliveryPersonnel.query.filter_by(user_id=rider_id).first()
    order = Order.query.get(order_id) if order_id else None
    
    return render_template('seller/rider_chat.html', 
                         chat_messages=chat_messages, 
                         rider=rider, 
                         rider_profile=rider_profile,
                         order=order,
                         seller_id=seller_id)
```

### Option 2: Use Chat API Directly (Alternative)
Instead of rendering a template, redirect to use the unified chat API:

```python
@app.route('/seller/chat/rider/<int:rider_id>')
@login_required
@seller_required
def seller_chat_rider(rider_id):
    """Redirect to unified chat interface"""
    # The unified chat API handles all user-to-user chats
    # Just redirect to a generic chat interface
    return redirect(url_for('unified_chat_interface', peer_id=rider_id))
```

### Update Template
Update `backend/templates/seller/rider_chat.html` to work with unified chat:

```html
<!-- Update the message display logic -->
{% for m in chat_messages %}
  {% set is_from_seller = (m.sender_id == seller_id) %}
  {% set is_from_rider = (m.sender_id == rider.id) %}
  <div class="rider-message-row {{ 'seller-side' if is_from_seller else 'rider-side' }}">
    <!-- Message content -->
    <div class="rider-message-bubble {{ 'seller' if is_from_seller else 'rider' }}">
      <div>{{ m.message }}</div>
    </div>
    <div class="rider-message-meta">
      {{ m.created_at.strftime('%Y-%m-%d %H:%M') }}
    </div>
  </div>
{% endfor %}
```

## Implementation Steps

1. **Backup current code**
   ```bash
   copy backend\app.py backend\app.py.backup
   ```

2. **Update the seller_chat_rider function** (around line 12263 in app.py)
   - Replace the function with Option 1 code above

3. **Update the template** (backend/templates/seller/rider_chat.html)
   - Change `m.buyer_id` and `m.sender_role` checks to `m.sender_id` checks
   - Remove references to `sender_role` field

4. **Test the fix**
   - Login as seller
   - Go to an order with assigned rider
   - Click "Chat with Rider"
   - Send a message
   - Login as rider
   - Check inbox - seller's message should appear
   - Reply as rider
   - Check seller's chat - rider's reply should appear

## Database Check
Verify the unified chat_message table exists:

```sql
SELECT * FROM chat_message WHERE sender_id IN (SELECT id FROM "user" WHERE role='seller') 
AND receiver_id IN (SELECT id FROM "user" WHERE role='rider') LIMIT 10;
```

## API Endpoints Available
The unified chat API already provides these endpoints:
- `GET /api/chat/conversations` - Get all conversations
- `GET /api/chat/messages/<user_id>` - Get messages with specific user
- `POST /api/chat/send` - Send a message
- `GET /api/chat/unread-count` - Get unread count

## Quick Fix Script
Create `backend/fix_seller_rider_chat.py`:

```python
"""
Quick fix to migrate old RiderChatMessage to unified chat_message table
"""
from app import app, db, RiderChatMessage
from datetime import datetime

def migrate_rider_messages():
    with app.app_context():
        # Get all old rider chat messages
        old_messages = RiderChatMessage.query.all()
        
        for old_msg in old_messages:
            # Create new unified message
            # Determine sender/receiver based on sender_role
            if old_msg.sender_role == 'buyer':
                sender_id = old_msg.buyer_id
                receiver_id = old_msg.rider_id
            else:  # rider
                sender_id = old_msg.rider_id
                receiver_id = old_msg.buyer_id
            
            # Insert into chat_message table
            db.session.execute(
                """INSERT INTO chat_message 
                   (sender_id, receiver_id, message, order_id, is_read, created_at)
                   VALUES (:sender, :receiver, :msg, :order, :read, :created)""",
                {
                    'sender': sender_id,
                    'receiver': receiver_id,
                    'msg': old_msg.message,
                    'order': old_msg.order_id,
                    'read': old_msg.is_read,
                    'created': old_msg.created_at
                }
            )
        
        db.session.commit()
        print(f"Migrated {len(old_messages)} messages to unified chat_message table")

if __name__ == '__main__':
    migrate_rider_messages()
```

Run with: `python backend/fix_seller_rider_chat.py`

## Testing Checklist
- [ ] Seller can send message to rider from order detail page
- [ ] Rider receives seller's message in inbox
- [ ] Rider can reply to seller
- [ ] Seller receives rider's reply
- [ ] Unread count updates correctly
- [ ] Real-time notifications work via Socket.IO
- [ ] Message history persists correctly
- [ ] No duplicate messages appear

## Files Modified
1. `backend/app.py` - seller_chat_rider function
2. `backend/templates/seller/rider_chat.html` - message display logic

## Related Files
- `backend/unified_chat_api.py` - Unified chat system (already working)
- `backend/templates/seller/order_detail.html` - Chat button link
- `mobile_app/lib/services/chat_service.dart` - Mobile chat service

## Success Criteria
✓ Seller messages appear in rider's inbox
✓ Rider messages appear in seller's chat
✓ All messages use unified chat_message table
✓ Real-time updates work via Socket.IO
✓ No errors in console or logs
