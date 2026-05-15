# UNIFIED CHAT SYSTEM - COMPLETE SETUP GUIDE

## Overview
Ang bagong unified chat system ay gumagana para sa LAHAT ng user types:
- ✅ Buyer ↔ Seller
- ✅ Buyer ↔ Rider
- ✅ Seller ↔ Rider
- ✅ Any user ↔ Any user

## Step 1: Run Database Migration

```bash
cd c:\Users\mnban\Documents\kids\backend
python migrate_unified_chat.py
```

Dapat makita mo:
```
✅ chat_message table created successfully
✅ Index created: idx_chat_sender
✅ Index created: idx_chat_receiver
✅ MIGRATION SUCCESSFUL
```

## Step 2: Update app.py

Hanapin ang line na:
```python
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    allow_upgrades=False,
)
```

Pagkatapos nito, idagdag:
```python
# Initialize Unified Chat System
from unified_chat_api import register_unified_chat
register_unified_chat(app, db, socketio)
```

## Step 3: Restart Flask Server

```bash
# Stop current server (Ctrl+C)
# Then start again:
python app.py
```

Dapat makita mo sa console:
```
✅ ChatMessage table ready
✅ Unified chat system registered
```

## Step 4: Test the API

### Get Conversations
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/chat/conversations
```

### Get Messages with User
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/chat/messages/123
```

### Send Message
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" \
  -d '{"receiver_id": 123, "message": "Hello!"}' \
  http://localhost:5000/api/chat/send
```

### Get Unread Count
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/chat/unread-count
```

## Mobile App Integration

Ang mobile app (Flutter) ay gumagamit na ng tamang endpoints:

### ChatService (lib/services/chat_service.dart)
- ✅ `/api/chat/conversations` - Already correct
- ✅ `/api/chat/messages/<user_id>` - Already correct
- ✅ `/api/chat/send` - Already correct
- ✅ `/api/chat/unread-count` - Already correct

### Socket.IO Events
- ✅ `join_chat` - User joins their room
- ✅ `new_message` - Receive new messages
- ✅ `typing` - Show typing indicator
- ✅ `stop_typing` - Hide typing indicator
- ✅ `user_typing` - Receive typing notification
- ✅ `user_stop_typing` - Receive stop typing notification

## Database Schema

```sql
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES "user"(id),
    receiver_id INTEGER NOT NULL REFERENCES "user"(id),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_chat_sender ON chat_message(sender_id);
CREATE INDEX idx_chat_receiver ON chat_message(receiver_id);
CREATE INDEX idx_chat_created ON chat_message(created_at DESC);
CREATE INDEX idx_chat_is_read ON chat_message(is_read) WHERE is_read = FALSE;
CREATE INDEX idx_chat_conversation ON chat_message(sender_id, receiver_id, created_at DESC);
```

## Features

### ✅ Real-time Messaging
- Socket.IO integration for instant message delivery
- Typing indicators
- Read receipts

### ✅ Conversation Management
- List all conversations with last message
- Unread message counts
- Sorted by most recent

### ✅ Message History
- Full conversation history
- Automatic read marking
- Chronological order

### ✅ Cross-Role Support
- Buyer can chat with Seller
- Buyer can chat with Rider
- Seller can chat with Rider
- Any combination works!

## Troubleshooting

### Problem: "chat_message table does not exist"
**Solution:** Run the migration script:
```bash
python migrate_unified_chat.py
```

### Problem: "Module 'unified_chat_api' not found"
**Solution:** Make sure `unified_chat_api.py` is in the backend folder

### Problem: Socket.IO not working
**Solution:** Check that socketio is initialized before registering chat:
```python
socketio = SocketIO(app, ...)  # Must be before
register_unified_chat(app, db, socketio)  # This line
```

### Problem: 401 Unauthorized
**Solution:** Make sure JWT token is included in Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Testing Checklist

- [ ] Database migration completed
- [ ] app.py updated with chat initialization
- [ ] Server restarted successfully
- [ ] Can get conversations list
- [ ] Can send messages
- [ ] Can receive messages in real-time
- [ ] Typing indicators work
- [ ] Unread counts update correctly
- [ ] Mobile app can connect and chat

## Support

Kung may problema, check ang console logs:
- Backend: `python app.py` output
- Mobile: Flutter debug console

Common log messages:
- ✅ `ChatMessage table ready` - Database OK
- ✅ `Unified chat system registered` - API OK
- ✅ `Socket.IO connected` - Real-time OK
- ❌ `Error fetching conversations` - Check authentication
- ❌ `Error sending message` - Check receiver_id exists

## Next Steps

After setup is complete:
1. Test buyer-to-seller chat
2. Test buyer-to-rider chat
3. Test seller-to-rider chat
4. Verify real-time updates work
5. Check mobile app integration

Tapos na! 🎉
