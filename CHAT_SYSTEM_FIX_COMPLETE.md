# Chat System Fix - Complete Summary

## Problem
The application was crashing with `NameError: name 'StoreChatMessage' is not defined` because the old chat models (`StoreChatMessage` and `RiderChatMessage`) were removed and replaced with a unified `ChatMessage` model, but several functions were still using the old models.

## Root Cause
The codebase migrated from separate chat tables to a unified chat system:
- **OLD**: `StoreChatMessage` (buyer-seller), `RiderChatMessage` (buyer-rider)
- **NEW**: `ChatMessage` (unified for all user-to-user conversations)

However, multiple functions in `app.py` were still referencing the old models.

## Fixes Applied

### 1. Updated `notifications_summary()` function (line ~8141)
**Before:**
```python
if user.role == 'seller':
    unread_chat = StoreChatMessage.query.filter_by(seller_id=user_id, sender_role='buyer', is_read=False).count()
elif user.role == 'buyer':
    unread_chat = StoreChatMessage.query.filter_by(...).count() + RiderChatMessage.query.filter_by(...).count()
```

**After:**
```python
ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
if ChatMessage:
    unread_chat = ChatMessage.query.filter_by(receiver_id=user_id, is_read=False).count()
```

### 2. Updated `chat_list()` function (line ~12923)
**Before:**
- Used `StoreChatMessage.seller_id`, `StoreChatMessage.buyer_id`
- Filtered by `sender_role='seller'` or `sender_role='buyer'`

**After:**
- Uses unified `ChatMessage` with `sender_id` and `receiver_id`
- Gets all conversations using `or_` and `and_` queries
- No more role-based filtering

### 3. Updated `chat_window()` function (line ~12946)
**Before:**
```python
chat_messages = StoreChatMessage.query.filter_by(buyer_id=buyer_id, seller_id=seller_id).order_by(...)
StoreChatMessage.query.filter_by(..., sender_role='seller').update({'is_read': True})
```

**After:**
```python
ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
chat_messages = ChatMessage.query.filter(
    or_(
        and_(ChatMessage.sender_id == buyer_id, ChatMessage.receiver_id == seller_id),
        and_(ChatMessage.sender_id == seller_id, ChatMessage.receiver_id == buyer_id)
    )
).order_by(ChatMessage.created_at.asc()).all()
```

### 4. Updated `seller_chat_with_buyer()` function (line ~13025)
**Before:**
- Used `StoreChatMessage` with `buyer_id`, `seller_id`, `sender_role`

**After:**
- Uses unified `ChatMessage` with `sender_id`, `receiver_id`
- No more `sender_role` field

### 5. Updated `rider_chat_thread()` function (line ~14847)
**Before:**
```python
RiderChatMessage.query.filter_by(buyer_id=buyer_id, rider_id=rider_id, sender_role='buyer', is_read=False).update(...)
thread = RiderChatMessage.query.filter_by(buyer_id=buyer_id, rider_id=rider_id).order_by(...)
```

**After:**
```python
ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
unread_msgs = ChatMessage.query.filter_by(sender_id=buyer_id, receiver_id=rider_id, is_read=False).all()
thread = ChatMessage.query.filter(or_(...)).order_by(ChatMessage.created_at.asc()).all()
```

### 6. Updated `buyer_rider_chat()` function (line ~14915)
**Before:**
- Used `RiderChatMessage` with `buyer_id`, `rider_id`, `sender_role`

**After:**
- Uses unified `ChatMessage` with `sender_id`, `receiver_id`

### 7. Fixed `unified_chat_api.py` Authentication
**Problem:** Mobile app was getting 404 errors because JWT token authentication wasn't working

**Fix:**
- Updated `get_current_user_id()` to support both JWT tokens (mobile) and sessions (web)
- Added proper JWT decoding with error handling
- All endpoints now use `get_current_user_id()` instead of `get_user_from_token()`

```python
def get_current_user_id():
    """Extract user_id from JWT token (mobile) or session (web)"""
    # Check if token_required already set current_user_id
    if hasattr(request, 'current_user_id'):
        return request.current_user_id
    
    # Try JWT token from Authorization header (mobile)
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            import jwt, os
            JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
            if JWT_SECRET_KEY:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                return payload.get('user_id')
        except Exception as e:
            print(f"[WARNING] JWT decode failed: {e}")
    
    # Fallback to session (web)
    from flask import session
    return session.get('user_id')
```

## Key Changes in Data Model

### Old Schema (StoreChatMessage)
```python
buyer_id (FK to user)
seller_id (FK to user)
sender_role ('buyer' or 'seller')
message
product_id (optional)
is_read
created_at
```

### New Schema (ChatMessage)
```python
sender_id (FK to user)
receiver_id (FK to user)
message
product_id (optional)
order_id (optional)
is_read
created_at
```

## Benefits of Unified System
1. **Simpler**: One table for all conversations (buyer-seller, buyer-rider, seller-rider)
2. **Flexible**: Any user can chat with any other user
3. **Consistent**: Same API for all chat types
4. **Scalable**: Easier to add new user roles

## Testing Checklist
- [ ] Web chat (buyer ↔ seller) works
- [ ] Web chat (buyer ↔ rider) works
- [ ] Mobile API `/api/v1/chat/conversations` returns 200
- [ ] Mobile API `/api/v1/chat/unread-count` returns 200
- [ ] Mobile API `/api/v1/chat/messages/<id>` returns 200
- [ ] Mobile API `/api/v1/chat/send` works
- [ ] Unread badge counts display correctly
- [ ] Real-time notifications work via Socket.IO

## Files Modified
1. `backend/app.py` - Updated 6 chat functions
2. `backend/unified_chat_api.py` - Fixed authentication for mobile API

## Next Steps
1. Restart the Flask backend server
2. Test web chat functionality
3. Test mobile app chat functionality
4. Verify unread counts are accurate
5. Check Socket.IO real-time updates

## Notes
- The `ChatMessage` model is defined in `unified_chat_api.py` and registered when `register_unified_chat_api()` is called
- The model is accessed via `db.Model.registry._class_registry.get('ChatMessage')` to avoid circular imports
- All chat functions now use `or_` and `and_` from SQLAlchemy for flexible queries
- The unified system supports product chats (via `product_id`) and order chats (via `order_id`)
