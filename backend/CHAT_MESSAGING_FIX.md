# Chat/Messaging System Fix Summary

## Issues Fixed

### 1. **404 Errors on Chat Routes**
- **Problem**: Chat API routes were not accessible via `/api/v1` prefix
- **Solution**: Added `/api/v1` route aliases for all chat endpoints in `unified_chat_api.py`
- **Fixed Routes**:
  - `/api/v1/chat/conversations` - Get all conversations
  - `/api/v1/chat/messages/<user_id>` - Get messages with specific user
  - `/api/v1/chat/send` - Send message

### 2. **400 Errors on Product Chat**
- **Problem**: Product chat required both `product_id` and `seller_id`, but mobile app only sent `product_id`
- **Solution**: Auto-fetch `seller_id` from product when not provided
- **Fixed Endpoints**:
  - `/api/v1/chat/product/start` - Now auto-fetches seller from product
  - `/api/v1/chat/product/send` - Now auto-fetches receiver from product

### 3. **Duplicate Route Registration**
- **Problem**: `start_product_chat` was registered in both `unified_chat_api.py` and `product_chat_api.py`
- **Solution**: Removed duplicate from `product_chat_api.py`, kept enhanced version in `unified_chat_api.py`

### 4. **AttributeError: 'Product' object has no attribute 'image_url'**
- **Problem**: Code tried to access `product.image_url` but Product model uses `image_filename`
- **Solution**: Changed to `getattr(product, 'image_url', None) or getattr(product, 'image_filename', None)`
- **Fixed in**:
  - `get_product_chat_messages()`
  - `get_product_conversations()`

## API Endpoints Now Working

### Unified Chat (Buyer ↔ Seller ↔ Rider)
```
GET  /api/v1/chat/conversations          - Get all conversations
GET  /api/v1/chat/messages/<user_id>     - Get messages with user
POST /api/v1/chat/send                   - Send message
GET  /api/v1/chat/unread-count           - Get unread count
```

### Product Chat (Buyer ↔ Seller about products)
```
POST /api/v1/chat/product/start                    - Start product chat
GET  /api/v1/chat/product/<product_id>/messages    - Get product messages
POST /api/v1/chat/product/send                     - Send product message
GET  /api/v1/chat/conversations/product            - Get product conversations
```

## Request/Response Examples

### Start Product Chat
**Request:**
```json
POST /api/v1/chat/product/start
{
  "product_id": 123,
  "message": "Is this still available?"
}
```
**Response:**
```json
{
  "success": true,
  "conversation": {
    "peer_id": 5,
    "product_id": 123
  }
}
```

### Send Message
**Request:**
```json
POST /api/v1/chat/send
{
  "receiver_id": 5,
  "message": "Hello!"
}
```
**Response:**
```json
{
  "success": true,
  "message": {
    "id": 1,
    "sender_id": 2,
    "receiver_id": 5,
    "message": "Hello!",
    "created_at": "2025-01-15T10:30:00"
  }
}
```

### Send Product Message
**Request:**
```json
POST /api/v1/chat/product/send
{
  "product_id": 123,
  "message": "What's the shipping cost?"
}
```
**Response:**
```json
{
  "success": true,
  "message": {
    "id": 2,
    "sender_id": 2,
    "receiver_id": 5,
    "message": "What's the shipping cost?",
    "product_id": 123,
    "created_at": "2025-01-15T10:31:00"
  }
}
```

## Testing

### Test Chat Functionality
1. **Buyer → Seller Chat**:
   ```bash
   # Start chat
   curl -X POST http://localhost:5000/api/v1/chat/product/start \
     -H "Authorization: Bearer <buyer_token>" \
     -H "Content-Type: application/json" \
     -d '{"product_id": 1, "message": "Hello"}'
   
   # Send message
   curl -X POST http://localhost:5000/api/v1/chat/send \
     -H "Authorization: Bearer <buyer_token>" \
     -H "Content-Type: application/json" \
     -d '{"receiver_id": 5, "message": "Is this available?"}'
   ```

2. **Get Conversations**:
   ```bash
   curl -X GET http://localhost:5000/api/v1/chat/conversations \
     -H "Authorization: Bearer <token>"
   ```

3. **Get Messages**:
   ```bash
   curl -X GET http://localhost:5000/api/v1/chat/messages/5 \
     -H "Authorization: Bearer <token>"
   ```

## Database Schema

### ChatMessage Table
```sql
CREATE TABLE chat_message (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    product_id INTEGER,
    order_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(id),
    FOREIGN KEY (receiver_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (order_id) REFERENCES order(id)
);
```

## Real-time Features (Socket.IO)

### Events
- `join_chat` - User joins their chat room
- `new_message` - New message received
- `typing` - User is typing
- `stop_typing` - User stopped typing

### Usage
```javascript
// Join chat room
socket.emit('join_chat');

// Listen for new messages
socket.on('new_message', (data) => {
  console.log('New message:', data);
});

// Send typing indicator
socket.emit('typing', { receiver_id: 5 });
```

## Files Modified
1. `unified_chat_api.py` - Added v1 routes, fixed product chat
2. `product_chat_api.py` - Removed duplicates, fixed image_url errors

## Next Steps
1. Test all endpoints with mobile app
2. Verify real-time messaging works
3. Check unread count badges
4. Test buyer-seller-rider chat flows
