# Product Chat Loading Fix - Complete Solution

## Problem Summary

1. **ProductChatScreen stuck loading** - Messages not appearing after sending
2. **Backend error** - `StoreChatMessage` model doesn't exist (legacy model removed)
3. **Chat conversations not showing product chats** - Only showing rider/buyer chats
4. **Messages not appearing in buyer's chat list** after successful send

## Root Causes

### 1. Backend Using Legacy Model
Lines 8484, 8746, 8796 in `app.py` still reference `StoreChatMessage` which was removed:
```python
unread_chat_count = StoreChatMessage.query.filter_by(seller_id=seller_id, is_read=False, sender_role='buyer').count()
```

This causes crashes when seller dashboard loads.

### 2. Product Chat API Working But Not Integrated
- `product_chat_api.py` is correctly registered and working
- Uses `chat_message` table with `product_id` column
- But `ChatConversationsScreen` only loads rider/buyer conversations
- Missing API call to fetch product conversations

### 3. Missing Product Conversations Endpoint Integration
The backend has `/api/v1/chat/conversations/product` endpoint but:
- Not called by Flutter app
- Not merged with regular conversations in UI

## Complete Fix

### Fix 1: Replace Legacy StoreChatMessage in Backend

**File:** `backend/app.py`

Replace all 3 occurrences (lines 8484, 8746, 8796):

```python
# OLD (BROKEN):
unread_chat_count = StoreChatMessage.query.filter_by(seller_id=seller_id, is_read=False, sender_role='buyer').count()

# NEW (FIXED):
from sqlalchemy import text
unread_chat_count = db.session.execute(text("""
    SELECT COUNT(*) FROM chat_message 
    WHERE receiver_id = :seller_id 
    AND is_read = FALSE 
    AND product_id IS NOT NULL
"""), {'seller_id': seller_id}).scalar() or 0
```

### Fix 2: Add Product Conversations to API Service

**File:** `mobile_app/lib/services/api_service.dart`

Add after `getProductChatMessages` method (around line 1110):

```dart
static Future<List<dynamic>> getProductConversations() async {
  try {
    final result = await request('GET', '/api/v1/chat/conversations/product');
    if (result is Map<String, dynamic> && result['conversations'] is List) {
      return result['conversations'] as List;
    }
    return [];
  } catch (e) {
    debugPrint('❌ Error fetching product conversations: $e');
    return [];
  }
}
```

### Fix 3: Merge Product Chats into Conversations Screen

**File:** `mobile_app/lib/screens/buyer_app/chat_conversations_screen.dart`

#### 3a. Update `_loadConversations()` method (around line 150):

```dart
Future<void> _loadConversations() async {
  setState(() => _isLoading = true);
  try {
    // Load both regular and product conversations
    final regularConversations = await ApiService.getChatConversations();
    final productConversations = await ApiService.getProductConversations();
    
    // Merge conversations
    final allConversations = [...regularConversations];
    
    // Add product conversations with proper format
    for (var productConv in productConversations) {
      final otherUser = productConv['other_user'] as Map<String, dynamic>?;
      if (otherUser != null) {
        allConversations.add({
          'peer_id': otherUser['id'],
          'peer_name': otherUser['name'],
          'peer_role': otherUser['role'],
          'peer_profile_picture': otherUser['profile_picture'],
          'last_message': '📦 ${productConv['product_name']}: ${productConv['last_message']}',
          'last_message_time': productConv['last_message_time'],
          'unread_count': productConv['unread_count'] ?? 0,
          'product_id': productConv['product_id'],
          'product_name': productConv['product_name'],
          'product_image': productConv['product_image'],
          'product_price': productConv['product_price'],
        });
      }
    }
    
    if (mounted) {
      // Sort conversations by latest message time (descending)
      allConversations.sort((a, b) {
        final aTime = a['last_message_time'] ?? a['created_at'] ?? '';
        final bTime = b['last_message_time'] ?? b['created_at'] ?? '';
        if (aTime.isEmpty || bTime.isEmpty) return 0;
        try {
          final aDateTime = DateTime.parse(aTime.toString());
          final bDateTime = DateTime.parse(bTime.toString());
          return bDateTime.compareTo(aDateTime);
        } catch (_) {
          return 0;
        }
      });

      setState(() {
        _conversations = allConversations;
        _filtered = allConversations;
        _isLoading = false;
      });
      _fadeController.forward(from: 0);
    }
  } catch (e) {
    debugPrint('Error loading conversations: $e');
    if (mounted) setState(() => _isLoading = false);
  }
}
```

#### 3b. Update `_buildConversationTile()` to handle product chats (around line 469):

```dart
Widget _buildConversationTile(dynamic conversation, int index) {
  final peerId = conversation['peer_id'] as int;
  final peerName = conversation['peer_name'] as String? ?? 'Unknown';
  final peerRole = conversation['peer_role'] as String? ?? '';
  final peerProfilePic = conversation['peer_profile_picture'] as String?;
  final lastMessage = conversation['last_message'] as String? ?? '';
  final unreadCount = conversation['unread_count'] as int? ?? 0;
  final timestamp = conversation['last_message_time'] as String?;
  final isUnread = unreadCount > 0;
  final roleColor = _roleColor(peerRole);
  
  // Check if this is a product conversation
  final productId = conversation['product_id'] as int?;
  final productName = conversation['product_name'] as String?;
  final productImage = conversation['product_image'] as String?;
  final productPrice = conversation['product_price'] as double?;
  final isProductChat = productId != null;

  return GestureDetector(
    onTap: () {
      HapticFeedback.lightImpact();
      
      // Navigate to appropriate chat screen
      if (isProductChat) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ProductChatScreen(
              productId: productId!,
              productName: productName ?? 'Product',
              productImage: productImage ?? '',
              productPrice: productPrice ?? 0.0,
              sellerId: peerId,
              sellerName: peerName,
              sellerAvatar: peerProfilePic,
            ),
          ),
        ).then((_) => _loadConversations());
      } else {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ChatScreen(
              otherUserId: peerId,
              otherUserName: peerName,
              otherUserRole: peerRole,
              otherUserProfilePicture: peerProfilePic,
            ),
          ),
        ).then((_) => _loadConversations());
      }
    },
    child: AnimatedContainer(
      // ... rest of the tile UI remains the same
    ),
  );
}
```

#### 3c. Add import at top of file:

```dart
import 'product_chat_screen.dart';
```

### Fix 4: Ensure ProductChatScreen Refreshes After Send

**File:** `mobile_app/lib/screens/buyer_app/product_chat_screen.dart`

The `_sendMessage()` method already calls `_loadMessages()` after success, which is correct. 
But ensure the success check is working:

```dart
Future<void> _sendMessage() async {
  final message = _messageController.text.trim();
  if (message.isEmpty || _isSending) return;

  setState(() => _isSending = true);
  _messageController.clear();

  try {
    final response = await ApiService.sendProductMessage(
      productId: widget.productId,
      message: message,
    );

    debugPrint('Send message response: $response'); // Debug log

    if (response['success'] == true && mounted) {
      // Wait a bit for backend to process
      await Future.delayed(const Duration(milliseconds: 300));
      await _loadMessages();
    } else {
      if (mounted) {
        ModernSnackBar.showError(
          context,
          response['error'] ?? 'Failed to send message',
        );
      }
    }
  } catch (e) {
    debugPrint('Error sending message: $e');
    if (mounted) {
      ModernSnackBar.showError(context, 'Failed to send message');
    }
  } finally {
    if (mounted) setState(() => _isSending = false);
  }
}
```

## Testing Steps

1. **Test Backend Fix:**
   ```bash
   cd backend
   python app.py
   ```
   - Visit seller dashboard - should not crash
   - Check console for errors

2. **Test Product Chat:**
   - Open buyer app
   - Go to product detail
   - Click message icon
   - Send a message
   - Message should appear immediately in chat
   - Go back to home > Messages tab
   - Product conversation should appear in list with 📦 icon

3. **Test Seller Side:**
   - Login as seller
   - Check dashboard - unread count should work
   - Open chat - should see buyer's product inquiry

## Expected Behavior After Fix

✅ Product chat messages appear immediately after sending
✅ Seller dashboard loads without errors
✅ Product conversations appear in buyer's Messages tab
✅ Product chats show with product context (name, image, price)
✅ Unread counts work for product chats
✅ Real-time updates via Socket.IO work

## Files Modified

1. `backend/app.py` - 3 lines (8484, 8746, 8796)
2. `mobile_app/lib/services/api_service.dart` - Add 1 method
3. `mobile_app/lib/screens/buyer_app/chat_conversations_screen.dart` - Update 2 methods, add import
4. `mobile_app/lib/screens/buyer_app/product_chat_screen.dart` - Minor enhancement (optional)
