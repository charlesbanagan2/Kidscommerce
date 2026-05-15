"""
CHAT SYSTEM DOCUMENTATION
=========================

This document describes the complete chat system implementation.

DATABASE STRUCTURE
------------------
Table: chat_message
- id: INTEGER (Primary Key)
- sender_id: INTEGER (Foreign Key -> user.id)
- receiver_id: INTEGER (Foreign Key -> user.id)
- message: TEXT (Message content)
- product_id: INTEGER (Foreign Key -> product.id, nullable)
- order_id: INTEGER (Foreign Key -> order.id, nullable)
- is_read: BOOLEAN (Read status)
- created_at: TIMESTAMP (Message timestamp)

CHAT TYPES
----------
1. Direct Chat (Unified Chat)
   - Any user can message any other user
   - No product_id or order_id
   - Supports: Buyer ↔ Seller, Buyer ↔ Rider, Seller ↔ Rider

2. Product Chat
   - Chat about a specific product
   - Has product_id set
   - Buyer asks seller about product
   - Product details shown in chat

3. Order Chat (Future)
   - Chat about a specific order
   - Has order_id set
   - Between buyer, seller, and rider

API ENDPOINTS
-------------

UNIFIED CHAT (Direct Messaging)
--------------------------------
1. GET /api/v1/chat/conversations
   - Get all conversations for current user
   - Returns list of conversations with last message and unread count

2. GET /api/v1/chat/messages/<user_id>
   - Get all messages with a specific user
   - Marks messages as read
   - Returns messages with sender info

3. POST /api/v1/chat/send
   - Send a direct message to another user
   - Body: { "receiver_id": int, "message": string }
   - Returns created message

4. GET /api/v1/chat/unread-count
   - Get total unread message count for current user
   - Returns: { "unread_count": int }

PRODUCT CHAT
------------
1. POST /api/v1/chat/product/start
   - Start a chat about a product
   - Body: { "product_id": int, "message": string (optional) }
   - Auto-detects seller from product
   - Returns conversation info

2. POST /api/v1/chat/product/send
   - Send a message about a product
   - Body: { "product_id": int, "message": string }
   - Auto-detects receiver (seller) from product
   - Returns created message

3. GET /api/v1/chat/product/<product_id>/messages
   - Get all messages about a specific product
   - Returns messages with product info
   - Marks messages as read

4. GET /api/v1/chat/conversations/product
   - Get all product conversations for current user
   - Returns list with product details

MOBILE APP IMPLEMENTATION
--------------------------

Files:
- lib/screens/buyer_app/product_chat_screen.dart
  * Shopee-style product chat screen
  * Shows product card at top
  * Message bubbles with timestamps
  * Real-time messaging

- lib/screens/buyer_app/chat_screen.dart
  * Generic direct chat screen
  * For non-product conversations

- lib/services/api_service.dart
  * API methods for all chat endpoints
  * startProductChat()
  * sendProductMessage()
  * getProductChatMessages()
  * getChatMessages()
  * sendChatMessageNew()

BACKEND IMPLEMENTATION
----------------------

Files:
- unified_chat_api.py
  * Handles direct messaging between any users
  * Defines ChatMessage model
  * Socket.IO support for real-time updates

- product_chat_api.py
  * Handles product-specific chats
  * Auto-detects seller from product
  * Shows product context in messages

- app.py
  * Registers both chat APIs
  * Legacy chat endpoints (StoreChatMessage, RiderChatMessage)

MESSAGE FLOW
------------

1. User clicks message icon on product
   ↓
2. App calls startProductChat(productId, message)
   ↓
3. Backend creates message in chat_message table
   - Sets product_id
   - Auto-detects seller_id from product
   - Sets sender_id from JWT token
   ↓
4. App navigates to ProductChatScreen
   - Shows product card at top
   - Loads messages via getProductChatMessages()
   ↓
5. User sends message
   ↓
6. App calls sendProductMessage(productId, message)
   ↓
7. Backend saves to chat_message table
   - Emits Socket.IO event for real-time update
   ↓
8. Receiver gets notification
   - Can view in chat screen
   - Product context always visible

DATA INTEGRITY
--------------
✓ All messages have valid sender_id and receiver_id
✓ All messages have timestamps
✓ All messages have is_read status
✓ Product messages have valid product_id
✓ Foreign key constraints ensure data integrity

FEATURES
--------
✓ Direct messaging between any users
✓ Product-specific chats with context
✓ Unread message counts
✓ Message read status
✓ Real-time updates via Socket.IO
✓ Conversation list with last message
✓ Message history
✓ Shopee-style product chat UI
✓ Seller can see all product inquiries
✓ Buyer can see product details in chat

TESTING
-------
Run these scripts to verify:
- python test_chat_persistence.py
  * Checks if messages are saved
  * Shows message statistics
  * Verifies data integrity

- python verify_chat_endpoints.py
  * Lists all chat endpoints
  * Verifies endpoint coverage
  * Checks database structure

- python test_chat_system.py
  * End-to-end testing
  * Tests all user combinations
  * Verifies message delivery

TROUBLESHOOTING
---------------
1. Messages not saving?
   - Check chat_message table exists
   - Verify foreign key constraints
   - Check user authentication

2. 500 errors?
   - Check Flask logs for errors
   - Verify database connection
   - Check model imports

3. Messages not showing?
   - Verify API endpoint is correct
   - Check user_id in JWT token
   - Verify database query

4. Slow performance?
   - Add indexes on sender_id, receiver_id
   - Add index on created_at
   - Add index on product_id

FUTURE ENHANCEMENTS
-------------------
- Order-specific chats
- Group chats
- File/image attachments
- Voice messages
- Message reactions
- Message search
- Chat archiving
- Block/report users
- Typing indicators
- Online status
- Message encryption
"""

print(__doc__)
