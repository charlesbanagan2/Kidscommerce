# PRODUCT CHAT FEATURE - TESTING GUIDE

## ✅ Implementation Complete

### Backend Changes
1. **unified_chat_api.py** - Added `product_id` and `order_id` columns to ChatMessage model
2. **product_chat_api.py** - Created new API endpoints for product chat
3. **app.py** - Registered product chat API

### Mobile App Changes
1. **product_detail_screen.dart** - Connected message icon to chat function
2. **api_service.dart** - Added product chat API methods

---

## 🔧 Backend API Endpoints

### 1. Start Product Chat
```
POST /api/v1/chat/product/start
Headers: Authorization: Bearer {token}
Body: {
  "product_id": 1,
  "message": "Hi! I'm interested in this product"
}

Response: {
  "success": true,
  "chat_started": true,
  "seller": {
    "id": 2,
    "name": "Seller Name",
    "profile_picture": "/uploads/..."
  },
  "product": {
    "id": 1,
    "name": "Product Name",
    "image": "/uploads/...",
    "price": 100.00
  }
}
```

### 2. Get Product Messages
```
GET /api/v1/chat/product/{product_id}/messages
Headers: Authorization: Bearer {token}

Response: {
  "success": true,
  "messages": [...],
  "product": {...}
}
```

### 3. Send Product Message
```
POST /api/v1/chat/product/send
Headers: Authorization: Bearer {token}
Body: {
  "product_id": 1,
  "receiver_id": 2,
  "message": "Is this still available?"
}

Response: {
  "success": true,
  "message": {...}
}
```

---

## 📱 Mobile App Testing Steps

### Step 1: Restart Backend
```bash
cd c:\Users\mnban\Documents\kids\backend
python app.py
```

Expected output:
```
[OK] Notification API registered
[OK] ChatMessage table ready
[OK] Unified chat system registered
[OK] Product chat API registered
```

### Step 2: Test in Mobile App

1. **Open Product Detail Screen**
   - Navigate to any product
   - Look for message icon (💬) in bottom bar

2. **Click Message Icon**
   - Should check if user is logged in
   - If not logged in: Show "Please log in to message the seller"
   - If logged in: Navigate to chat screen

3. **Chat Screen Opens**
   - Should show seller name/logo
   - Should show chat interface
   - Can send messages about the product

### Step 3: Verify Database

Check if messages are saved with product_id:
```sql
SELECT id, sender_id, receiver_id, product_id, message, created_at 
FROM chat_message 
WHERE product_id IS NOT NULL
ORDER BY created_at DESC;
```

---

## 🐛 Troubleshooting

### Error: "Failed to start chat"

**Possible Causes:**
1. Backend not running
2. User not logged in
3. Product has no seller_id
4. Network connection issue

**Solutions:**
1. Check backend is running on port 5000
2. Verify user is authenticated
3. Check product data has valid seller_id
4. Check mobile app baseUrl configuration

### Error: "Seller information not available"

**Cause:** Product doesn't have seller_id

**Solution:** 
```sql
UPDATE product SET seller_id = 2 WHERE seller_id IS NULL;
```

### Error: Database connection timeout

**Cause:** Supabase connection issue

**Solution:** Backend will use local ORM fallback automatically

---

## ✅ Success Indicators

1. **Backend Console:**
   ```
   [OK] Product chat API registered
   ```

2. **Mobile App:**
   - Message icon is clickable
   - Navigates to chat screen
   - Can send/receive messages

3. **Database:**
   - Messages saved with product_id
   - Real-time updates via Socket.IO

---

## 📊 Feature Flow

```
User clicks message icon
    ↓
Check if logged in
    ↓
Call ApiService.startProductChat()
    ↓
Backend creates chat_message with product_id
    ↓
Navigate to ChatScreen with seller info
    ↓
User can chat about the product
    ↓
Seller sees message with product context
```

---

## 🎯 Testing Checklist

- [ ] Backend starts without errors
- [ ] Product chat API registered
- [ ] Message icon visible in product detail
- [ ] Click message icon (not logged in) → shows login error
- [ ] Login as buyer
- [ ] Click message icon → navigates to chat
- [ ] Chat screen shows seller info
- [ ] Can send message
- [ ] Message saved in database with product_id
- [ ] Seller can see message (if testing as seller)

---

## 📝 Notes

- Messages are saved with `product_id` for context
- Seller can see which product the buyer is asking about
- Real-time notifications via Socket.IO
- Works with existing chat screen
- No changes needed to chat_screen.dart

---

## 🚀 Ready to Test!

1. Restart backend: `python app.py`
2. Run mobile app
3. Navigate to product detail
4. Click message icon
5. Start chatting!

