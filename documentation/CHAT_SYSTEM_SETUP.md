# 💬 COMPLETE CHAT SYSTEM - SETUP GUIDE

## ✅ FEATURES

### All User Roles Supported
- ✅ **Buyer ↔ Seller** - Chat about products and orders
- ✅ **Buyer ↔ Rider** - Chat about delivery
- ✅ **Buyer ↔ Admin** - Customer support
- ✅ **Seller ↔ Admin** - Seller support
- ✅ **Rider ↔ Admin** - Rider support
- ✅ **Profile Pictures** - Display in all conversations
- ✅ **Real-time Messaging** - Socket.IO integration
- ✅ **Typing Indicators** - See when someone is typing
- ✅ **Unread Counts** - Badge notifications
- ✅ **Message History** - Full conversation history

---

## 🚀 QUICK START (3 STEPS)

### Step 1: Database Migration (2 minutes)
```bash
cd backend
python add_chat_table.py
```

### Step 2: Backend Integration (3 minutes)

Add to `backend/app.py` (before `if __name__ == '__main__':`):

```python
# ============================================
# CHAT SYSTEM INTEGRATION
# ============================================
exec(open('chat_complete_api.py').read())
print("✅ Chat API loaded successfully")
```

### Step 3: Mobile App (Already Complete!)

Files created:
- ✅ `lib/services/chat_service.dart`
- ✅ `lib/screens/chat/chat_conversations_screen.dart`
- ✅ `lib/screens/chat/chat_screen.dart`

---

## 📊 DATABASE SCHEMA

### ChatMessage Table
```sql
CREATE TABLE chat_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(id),
    FOREIGN KEY (receiver_id) REFERENCES user(id)
);

-- Indexes for performance
CREATE INDEX idx_chat_sender ON chat_message(sender_id);
CREATE INDEX idx_chat_receiver ON chat_message(receiver_id);
CREATE INDEX idx_chat_created ON chat_message(created_at);
CREATE INDEX idx_chat_is_read ON chat_message(is_read);
```

---

## 🔌 API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/conversations` | Get all conversations |
| GET | `/api/chat/messages/<user_id>` | Get messages with user |
| POST | `/api/chat/send` | Send a message |
| POST | `/api/chat/mark-read/<user_id>` | Mark messages as read |
| GET | `/api/chat/unread-count` | Get unread count |
| GET | `/api/chat/search-users` | Search users to chat |
| GET | `/api/chat/order/<order_id>/partner` | Get chat partner for order |

---

## 🔄 SOCKET.IO EVENTS

### Client → Server
- `join_chat` - Join personal chat room
- `typing` - User is typing
- `stop_typing` - User stopped typing

### Server → Client
- `joined_chat` - Successfully joined
- `new_message` - New message received
- `user_typing` - Other user is typing
- `user_stop_typing` - Other user stopped typing

---

## 📱 MOBILE APP USAGE

### Navigate to Chat
```dart
// From anywhere in the app
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => ChatConversationsScreen(),
  ),
);
```

### Chat with Specific User
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => ChatScreen(
      otherUserId: userId,
      otherUserName: 'John Doe',
      otherUserRole: 'seller',
      otherUserProfilePicture: '/uploads/profile.jpg',
    ),
  ),
);
```

### Chat from Order
```dart
// Get chat partner for order
final result = await ChatService.getOrderChatPartner(accessToken, orderId);
if (result['success'] == true) {
  final partner = result['partner'];
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => ChatScreen(
        otherUserId: partner['id'],
        otherUserName: partner['name'],
        otherUserRole: partner['role'],
        otherUserProfilePicture: partner['profile_picture'],
      ),
    ),
  );
}
```

---

## 🎨 UI FEATURES

### Conversations List
- ✅ Profile pictures with fallback initials
- ✅ Role badges (Seller, Rider, Admin)
- ✅ Last message preview
- ✅ Unread count badges
- ✅ Time formatting (Today, Yesterday, Date)
- ✅ Pull-to-refresh
- ✅ Real-time updates

### Chat Screen
- ✅ Profile picture in app bar
- ✅ Message bubbles (sent/received)
- ✅ Typing indicators
- ✅ Auto-scroll to bottom
- ✅ Time stamps
- ✅ Send button with loading state
- ✅ Real-time message delivery

---

## 🧪 TESTING

### Test 1: Database Migration
```bash
python add_chat_table.py
```
Expected: "✅ Chat system database migration completed!"

### Test 2: Send Message (API)
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_id": 2, "message": "Hello!"}'
```

### Test 3: Mobile App
1. Login as buyer
2. Navigate to chat
3. Search for seller
4. Send message
5. Login as seller (different device)
6. See message in real-time

---

## 🔐 SECURITY

- ✅ JWT authentication required
- ✅ Users can only see their own conversations
- ✅ Messages marked as read automatically
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention (JSON responses)
- ✅ Input validation

---

## 💡 USE CASES

### Buyer → Seller
```
Buyer: "Is this product available in blue?"
Seller: "Yes! We have it in stock."
Buyer: "Great! I'll order it now."
```

### Buyer → Rider
```
Buyer: "Where are you now?"
Rider: "I'm 5 minutes away from your location."
Buyer: "Thanks! I'll wait outside."
```

### Buyer → Admin
```
Buyer: "I haven't received my refund yet."
Admin: "Let me check your order. One moment please."
Admin: "Your refund has been processed. It will reflect in 3-5 days."
```

### Seller → Admin
```
Seller: "How do I update my store information?"
Admin: "Go to Settings > Store Profile > Edit."
Seller: "Thank you!"
```

---

## 🎯 INTEGRATION POINTS

### Add Chat Button to Order Details
```dart
ElevatedButton.icon(
  onPressed: () async {
    final result = await ChatService.getOrderChatPartner(
      accessToken,
      order.id,
    );
    if (result['success'] == true) {
      final partner = result['partner'];
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ChatScreen(
            otherUserId: partner['id'],
            otherUserName: partner['name'],
            otherUserRole: partner['role'],
            otherUserProfilePicture: partner['profile_picture'],
          ),
        ),
      );
    }
  },
  icon: Icon(Icons.chat),
  label: Text('Chat with ${userRole}'),
)
```

### Add Chat Badge to Navigation
```dart
BottomNavigationBarItem(
  icon: Stack(
    children: [
      Icon(Icons.chat),
      if (unreadCount > 0)
        Positioned(
          right: 0,
          top: 0,
          child: Container(
            padding: EdgeInsets.all(2),
            decoration: BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
            ),
            child: Text(
              unreadCount.toString(),
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
              ),
            ),
          ),
        ),
    ],
  ),
  label: 'Messages',
)
```

---

## 🔧 TROUBLESHOOTING

### Issue: "chat_message table does not exist"
```bash
python add_chat_table.py
```

### Issue: Socket.IO not connecting
Check CORS in app.py:
```python
socketio = SocketIO(app, cors_allowed_origins="*")
```

### Issue: Profile pictures not showing
Verify User model has `profile_picture` column:
```python
profile_picture = db.Column(db.String(255), nullable=True)
```

### Issue: Messages not real-time
1. Check Socket.IO connection in mobile app
2. Verify `join_chat` event is emitted
3. Check backend logs for Socket.IO errors

---

## 📈 PERFORMANCE

### Database Indexes
- ✅ Sender ID index
- ✅ Receiver ID index
- ✅ Created at index
- ✅ Is read index

### Optimizations
- ✅ Limit conversations query (20 users)
- ✅ Efficient message queries (sender/receiver filter)
- ✅ Auto-mark as read on view
- ✅ Socket.IO for real-time (no polling)

---

## ✅ SUCCESS CHECKLIST

- [ ] Database migration completed
- [ ] Backend API integrated
- [ ] Mobile app files created
- [ ] Can send message (buyer → seller)
- [ ] Can send message (buyer → rider)
- [ ] Can send message (buyer → admin)
- [ ] Profile pictures display
- [ ] Real-time messaging works
- [ ] Typing indicators work
- [ ] Unread counts accurate
- [ ] Messages saved to database

---

## 🎉 CONGRATULATIONS!

You now have a complete chat system with:
- ✅ All user roles supported
- ✅ Profile pictures
- ✅ Real-time messaging
- ✅ Typing indicators
- ✅ Unread counts
- ✅ Full message history
- ✅ Beautiful UI

**Start chatting!** 💬
