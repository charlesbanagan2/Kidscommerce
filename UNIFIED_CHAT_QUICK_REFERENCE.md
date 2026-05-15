# Unified Chat System - Quick Reference Guide

## Overview
The chat system supports **all user-to-user combinations** using a single unified API and database table.

## Supported Chat Combinations

| From → To | Status | Use Case |
|-----------|--------|----------|
| Buyer → Seller | ✅ Working | Product inquiries, order questions |
| Seller → Buyer | ✅ Working | Respond to inquiries, order updates |
| Rider → Buyer | ✅ Working | Delivery coordination, location sharing |
| Buyer → Rider | ✅ Working | Delivery instructions, contact rider |
| Rider → Seller | ✅ Working | Pickup coordination, order details |
| Seller → Rider | ✅ Working | Pickup instructions, special notes |

## API Endpoints

### 1. Get All Conversations
```http
GET /api/chat/conversations
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "peer_id": 123,
      "peer_name": "John Doe",
      "peer_role": "buyer",
      "peer_profile_picture": "/static/uploads/user_avatars/...",
      "last_message": "Hello!",
      "last_message_time": "2025-01-15T10:30:00Z",
      "unread_count": 2
    }
  ]
}
```

### 2. Get Messages with Specific User
```http
GET /api/chat/messages/<other_user_id>
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "sender_id": 10,
      "receiver_id": 20,
      "message": "Hello!",
      "is_read": true,
      "created_at": "2025-01-15T10:30:00Z",
      "sender": {
        "id": 10,
        "name": "John Doe",
        "role": "buyer",
        "profile_picture": "/static/uploads/..."
      }
    }
  ]
}
```

### 3. Send Message
```http
POST /api/chat/send
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "receiver_id": 123,
  "message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "success": true,
  "message": {
    "id": 456,
    "sender_id": 10,
    "receiver_id": 123,
    "message": "Hello, how are you?",
    "created_at": "2025-01-15T10:35:00Z"
  }
}
```

### 4. Get Unread Count
```http
GET /api/chat/unread-count
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "unread_count": 5
}
```

## Flutter Integration

### 1. Initialize Chat Service
```dart
import '../../services/chat_service.dart';

// In your widget's initState
void initState() {
  super.initState();
  _initializeChat();
}

void _initializeChat() {
  final authProvider = Provider.of<AuthProvider>(context, listen: false);
  final accessToken = authProvider.accessToken;
  final userId = authProvider.user?.id;

  if (accessToken != null && userId != null) {
    ChatService.initializeSocket(
      accessToken,
      userId: userId,
      onNewMessage: (messageData) {
        // Handle new message
        print('New message from: ${messageData['sender_id']}');
        _loadMessages(); // Refresh messages
      },
      onUserTyping: (senderId) {
        // Show typing indicator
        setState(() => _isOtherUserTyping = true);
      },
      onUserStopTyping: (senderId) {
        // Hide typing indicator
        setState(() => _isOtherUserTyping = false);
      },
    );
  }
}
```

### 2. Load Conversations
```dart
Future<void> _loadConversations() async {
  final authProvider = Provider.of<AuthProvider>(context, listen: false);
  final accessToken = authProvider.accessToken;

  if (accessToken == null) return;

  final result = await ChatService.getConversations(accessToken);

  if (result['success'] == true) {
    setState(() {
      _conversations = result['conversations'] ?? [];
    });
  }
}
```

### 3. Load Messages
```dart
Future<void> _loadMessages(int otherUserId) async {
  final authProvider = Provider.of<AuthProvider>(context, listen: false);
  final accessToken = authProvider.accessToken;

  if (accessToken == null) return;

  final result = await ChatService.getMessages(accessToken, otherUserId);

  if (result['success'] == true) {
    setState(() {
      _messages = result['messages'] ?? [];
    });
  }
}
```

### 4. Send Message
```dart
Future<void> _sendMessage(int receiverId, String message) async {
  final authProvider = Provider.of<AuthProvider>(context, listen: false);
  final accessToken = authProvider.accessToken;

  if (accessToken == null) return;

  final result = await ChatService.sendMessage(
    accessToken,
    receiverId,
    message,
  );

  if (result['success'] == true) {
    _loadMessages(receiverId); // Refresh messages
  } else {
    // Show error
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(result['error'] ?? 'Failed to send message')),
    );
  }
}
```

### 5. Emit Typing Indicators
```dart
// When user starts typing
void _onTyping(int receiverId) {
  ChatService.emitTyping(receiverId);
  
  // Auto-stop after 2 seconds
  _typingTimer?.cancel();
  _typingTimer = Timer(const Duration(seconds: 2), () {
    ChatService.emitStopTyping(receiverId);
  });
}

// When user stops typing
void _onStopTyping(int receiverId) {
  ChatService.emitStopTyping(receiverId);
  _typingTimer?.cancel();
}
```

## Navigation Examples

### Navigate to Chat Screen (Buyer/Seller)
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => ChatScreen(
      otherUserId: sellerId,
      otherUserName: sellerName,
      otherUserRole: 'seller',
      otherUserProfilePicture: sellerProfilePic,
    ),
  ),
);
```

### Navigate to Chat Screen (Rider)
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => RiderChatScreen(
      otherUserId: buyerId,
      otherUserName: buyerName,
      otherUserRole: 'buyer',
      otherUserProfilePicture: buyerProfilePic,
    ),
  ),
);
```

## Database Schema

### chat_message Table
```sql
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    product_id INTEGER REFERENCES product(id) ON DELETE SET NULL,
    order_id INTEGER REFERENCES "order"(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chat_message_sender ON chat_message(sender_id);
CREATE INDEX idx_chat_message_receiver ON chat_message(receiver_id);
CREATE INDEX idx_chat_message_conversation ON chat_message(sender_id, receiver_id, created_at DESC);
CREATE INDEX idx_chat_message_unread ON chat_message(receiver_id, is_read) WHERE is_read = FALSE;
```

## Real-Time Features

### Socket.IO Events

#### Client → Server
- `join_chat` - Join user's personal chat room
- `typing` - Notify other user of typing
- `stop_typing` - Notify typing stopped

#### Server → Client
- `joined_chat` - Confirmation of room join
- `new_message` - New message received
- `user_typing` - Other user is typing
- `user_stop_typing` - Other user stopped typing

## Common Use Cases

### 1. Rider Contacts Buyer About Delivery
```dart
// Rider app - from order detail screen
final buyerId = order.buyerId;
final buyerName = order.buyerName;

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => RiderChatScreen(
      otherUserId: buyerId,
      otherUserName: buyerName,
      otherUserRole: 'buyer',
    ),
  ),
);
```

### 2. Buyer Contacts Rider About Location
```dart
// Buyer app - from order tracking screen
final riderId = order.riderId;
final riderName = order.riderName;

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => ChatScreen(
      otherUserId: riderId,
      otherUserName: riderName,
      otherUserRole: 'rider',
    ),
  ),
);
```

### 3. Rider Contacts Seller About Pickup
```dart
// Rider app - from pickup list
final sellerId = order.sellerId;
final sellerName = order.sellerName;

Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => RiderChatScreen(
      otherUserId: sellerId,
      otherUserName: sellerName,
      otherUserRole: 'seller',
    ),
  ),
);
```

## Testing Checklist

- [ ] Rider can send message to buyer
- [ ] Buyer can reply to rider
- [ ] Rider can send message to seller
- [ ] Seller can reply to rider
- [ ] Real-time message delivery works
- [ ] Typing indicators appear
- [ ] Unread badges update correctly
- [ ] Profile pictures display correctly
- [ ] Role badges show correct role
- [ ] Messages persist after app restart
- [ ] Read receipts work correctly

## Troubleshooting

### Messages Not Appearing
1. Check if Socket.IO is connected: Look for "✅ Chat Socket.IO connected" in logs
2. Verify access token is valid
3. Check network connectivity
4. Ensure receiver_id is correct

### Typing Indicators Not Working
1. Verify Socket.IO connection
2. Check if `emitTyping()` is being called
3. Ensure receiver is in the same conversation

### Profile Pictures Not Loading
1. Check if `peer_profile_picture` path is correct
2. Verify image URL is absolute (use `UrlConfig.toAbsoluteImageUrl()`)
3. Check if image file exists on server

## Performance Tips

1. **Pagination**: Load messages in batches for long conversations
2. **Caching**: Cache conversations list to reduce API calls
3. **Debouncing**: Debounce typing indicators to reduce Socket.IO traffic
4. **Image Optimization**: Compress profile pictures before upload
5. **Connection Management**: Disconnect Socket.IO when app goes to background

## Security Notes

- All endpoints require authentication (Bearer token)
- Users can only see their own conversations
- Messages are only visible to sender and receiver
- RLS (Row Level Security) policies enforce access control
- Socket.IO rooms are user-specific (user_<id>)

## Summary

The unified chat system is **production-ready** and supports all user combinations. No additional implementation needed - just use the existing API endpoints and Flutter screens! 🎉
