# Unified Chat System - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         UNIFIED CHAT SYSTEM                                  │
│                    (Already Implemented & Working!)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              MOBILE APP (Flutter)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │   Buyer      │    │    Seller    │    │    Rider     │                 │
│  │   Screens    │    │   Screens    │    │   Screens    │                 │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤                 │
│  │ • Chat       │    │ • Inbox      │    │ • Messages   │                 │
│  │ • Messages   │    │ • Messages   │    │ • Chat       │                 │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                 │
│         │                    │                    │                          │
│         └────────────────────┼────────────────────┘                          │
│                              │                                               │
│                    ┌─────────▼─────────┐                                    │
│                    │   ChatService     │                                    │
│                    │  (chat_service.   │                                    │
│                    │      dart)        │                                    │
│                    └─────────┬─────────┘                                    │
│                              │                                               │
└──────────────────────────────┼───────────────────────────────────────────────┘
                               │
                               │ HTTP/REST + Socket.IO
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│                         BACKEND (Python/Flask)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                    ┌──────────────────────────┐                             │
│                    │  unified_chat_api.py     │                             │
│                    │  (Main Chat Controller)  │                             │
│                    └────────┬─────────────────┘                             │
│                             │                                                │
│         ┌───────────────────┼───────────────────┐                           │
│         │                   │                   │                           │
│    ┌────▼────┐         ┌───▼────┐         ┌───▼────┐                      │
│    │  REST   │         │ Socket │         │  Auth  │                      │
│    │   API   │         │  .IO   │         │ Token  │                      │
│    │         │         │        │         │ Check  │                      │
│    └────┬────┘         └───┬────┘         └───┬────┘                      │
│         │                  │                  │                             │
│         │                  │                  │                             │
│    ┌────▼──────────────────▼──────────────────▼────┐                      │
│    │           API Endpoints                        │                      │
│    ├────────────────────────────────────────────────┤                      │
│    │ • GET  /api/chat/conversations                 │                      │
│    │ • GET  /api/chat/messages/<user_id>           │                      │
│    │ • POST /api/chat/send                          │                      │
│    │ • GET  /api/chat/unread-count                  │                      │
│    └────────────────────┬───────────────────────────┘                      │
│                         │                                                   │
└─────────────────────────┼───────────────────────────────────────────────────┘
                          │
                          │ SQL Queries
                          │
┌─────────────────────────▼───────────────────────────────────────────────────┐
│                      DATABASE (PostgreSQL/Supabase)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                    ┌──────────────────────────┐                             │
│                    │    chat_message table    │                             │
│                    ├──────────────────────────┤                             │
│                    │ • id (primary key)       │                             │
│                    │ • sender_id → user.id    │                             │
│                    │ • receiver_id → user.id  │                             │
│                    │ • message (text)         │                             │
│                    │ • product_id (optional)  │                             │
│                    │ • order_id (optional)    │                             │
│                    │ • is_read (boolean)      │                             │
│                    │ • created_at (timestamp) │                             │
│                    └────────┬─────────────────┘                             │
│                             │                                                │
│                    ┌────────▼─────────┐                                     │
│                    │   user table     │                                     │
│                    ├──────────────────┤                                     │
│                    │ • id             │                                     │
│                    │ • first_name     │                                     │
│                    │ • last_name      │                                     │
│                    │ • role           │                                     │
│                    │ • profile_pic    │                                     │
│                    └──────────────────┘                                     │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHAT FLOW EXAMPLES                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. RIDER → BUYER CHAT
   ┌────────┐                                              ┌────────┐
   │ Rider  │  "Hello, I'm on my way!"                    │ Buyer  │
   │  App   │ ─────────────────────────────────────────>  │  App   │
   └────────┘                                              └────────┘
        │                                                       │
        │ POST /api/chat/send                                  │
        │ {receiver_id: buyer_id, message: "..."}             │
        ▼                                                       │
   ┌─────────────────────────────────────────────────────┐   │
   │              Backend Server                          │   │
   │  1. Validate token                                   │   │
   │  2. Insert to chat_message table                     │   │
   │  3. Emit Socket.IO event                             │   │
   └─────────────────────────────────────────────────────┘   │
                                                               │
        Socket.IO: 'new_message' event ──────────────────────>│
                                                               │
   ┌────────┐                                              ┌────────┐
   │ Rider  │  <──────────────────────────────────────────│ Buyer  │
   │  App   │  "Thank you! I'll be waiting."              │  App   │
   └────────┘                                              └────────┘


2. RIDER → SELLER CHAT
   ┌────────┐                                              ┌────────┐
   │ Rider  │  "Where should I pick up the order?"        │ Seller │
   │  App   │ ─────────────────────────────────────────>  │  App   │
   └────────┘                                              └────────┘
        │                                                       │
        │ POST /api/chat/send                                  │
        │ {receiver_id: seller_id, message: "..."}            │
        ▼                                                       │
   ┌─────────────────────────────────────────────────────┐   │
   │              Backend Server                          │   │
   │  1. Validate token                                   │   │
   │  2. Insert to chat_message table                     │   │
   │  3. Emit Socket.IO event                             │   │
   └─────────────────────────────────────────────────────┘   │
                                                               │
        Socket.IO: 'new_message' event ──────────────────────>│
                                                               │
   ┌────────┐                                              ┌────────┐
   │ Rider  │  <──────────────────────────────────────────│ Seller │
   │  App   │  "Come to the back entrance"                │  App   │
   └────────┘                                              └────────┘


3. BUYER → SELLER CHAT (Already Working)
   ┌────────┐                                              ┌────────┐
   │ Buyer  │  "Is this product available?"               │ Seller │
   │  App   │ ─────────────────────────────────────────>  │  App   │
   └────────┘                                              └────────┘
        │                                                       │
        │ POST /api/chat/send                                  │
        ▼                                                       │
   ┌─────────────────────────────────────────────────────┐   │
   │              Backend Server                          │   │
   └─────────────────────────────────────────────────────┘   │
                                                               │
        Socket.IO: 'new_message' event ──────────────────────>│
                                                               │
   ┌────────┐                                              ┌────────┐
   │ Buyer  │  <──────────────────────────────────────────│ Seller │
   │  App   │  "Yes! We have stock."                      │  App   │
   └────────┘                                              └────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME FEATURES                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. TYPING INDICATORS
   User A starts typing
        │
        │ Socket.IO: emit('typing', {receiver_id: B})
        ▼
   Backend Server
        │
        │ Socket.IO: emit('user_typing', {sender_id: A}) to room_B
        ▼
   User B sees "User A is typing..."


2. READ RECEIPTS
   User A sends message
        │
        │ Message saved with is_read = false
        ▼
   User B opens conversation
        │
        │ GET /api/chat/messages/<A>
        │ Backend marks messages as read (is_read = true)
        ▼
   User A sees double check mark (✓✓)


3. ONLINE STATUS
   User connects
        │
        │ Socket.IO: emit('join_chat')
        ▼
   Backend adds user to online users
        │
        │ Broadcasts online status
        ▼
   Other users see green dot


┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATABASE RELATIONSHIPS                                │
└─────────────────────────────────────────────────────────────────────────────┘

chat_message
    ├── sender_id ──────> user.id (Rider/Buyer/Seller)
    ├── receiver_id ────> user.id (Rider/Buyer/Seller)
    ├── product_id ─────> product.id (optional, for product chats)
    └── order_id ───────> order.id (optional, for order chats)

user
    ├── role: 'buyer' | 'seller' | 'rider'
    ├── profile_picture
    └── seller_application.store_logo (for sellers)


┌─────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY & PERMISSIONS                                │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Authentication Required
   - All endpoints require Bearer token
   - Token validated on every request

✅ Authorization
   - Users can only see their own conversations
   - Can only send messages as themselves
   - Can only read messages sent to them

✅ Row Level Security (RLS)
   - Database enforces access control
   - Users can only query their own messages
   - Prevents unauthorized access

✅ Socket.IO Security
   - User-specific rooms (user_<id>)
   - Token validation on connection
   - Events only sent to authorized users


┌─────────────────────────────────────────────────────────────────────────────┐
│                        PERFORMANCE OPTIMIZATIONS                             │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Database Indexes
   - idx_chat_message_sender (sender_id)
   - idx_chat_message_receiver (receiver_id)
   - idx_chat_message_conversation (sender_id, receiver_id, created_at)
   - idx_chat_message_unread (receiver_id, is_read)

✅ Caching
   - Sender info cached during message fetch
   - Profile pictures cached in app

✅ Real-Time
   - Socket.IO for instant delivery
   - No polling required
   - Efficient event-based updates

✅ Pagination Ready
   - Can add limit/offset to queries
   - Load messages in batches
   - Infinite scroll support


┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUMMARY                                               │
└─────────────────────────────────────────────────────────────────────────────┘

✅ COMPLETE IMPLEMENTATION
   - Backend: unified_chat_api.py
   - Database: chat_message table
   - Mobile: ChatService + Screens
   - Real-time: Socket.IO

✅ SUPPORTED COMBINATIONS
   - Rider ↔ Buyer
   - Rider ↔ Seller
   - Buyer ↔ Seller

✅ FEATURES
   - Real-time messaging
   - Read receipts
   - Typing indicators
   - Online status
   - Profile pictures
   - Role badges
   - Unread counts

✅ PRODUCTION READY
   - Secure
   - Performant
   - Scalable
   - Tested

🎉 NO ADDITIONAL WORK NEEDED! 🎉
```
