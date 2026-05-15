# Chat System Test Guide

## Test Scenarios for Rider ↔ Buyer & Rider ↔ Seller Chat

### Prerequisites
- Backend server running (`python app.py`)
- Mobile app running (Flutter)
- Test accounts:
  - 1 Buyer account
  - 1 Seller account
  - 1 Rider account
- At least 1 order with rider assigned

---

## Test Scenario 1: Rider → Buyer Communication

### Setup
1. Create an order as buyer
2. Assign rider to the order
3. Login as rider

### Test Steps

#### Step 1: Rider Initiates Chat
1. **Action**: Login as rider
2. **Navigate**: Go to Messages/Chat screen
3. **Expected**: See buyer in conversations list
4. **Verify**:
   - ✅ Buyer name displays correctly
   - ✅ Buyer profile picture shows
   - ✅ "Buyer" role badge appears
   - ✅ Online status indicator shows

#### Step 2: Rider Sends Message
1. **Action**: Tap on buyer conversation
2. **Action**: Type "Hello, I'm on my way to deliver your order!"
3. **Action**: Tap send button
4. **Expected**: Message appears in chat
5. **Verify**:
   - ✅ Message shows in chat bubble
   - ✅ Timestamp displays
   - ✅ "Sent" indicator appears (double check mark)
   - ✅ Message saved to database

#### Step 3: Buyer Receives Message
1. **Action**: Login as buyer (different device/browser)
2. **Navigate**: Go to Messages screen
3. **Expected**: See unread message badge
4. **Verify**:
   - ✅ Unread count shows "1"
   - ✅ Rider appears in conversations list
   - ✅ Last message preview shows
   - ✅ "Rider" role badge displays

#### Step 4: Buyer Replies
1. **Action**: Tap on rider conversation
2. **Expected**: See rider's message
3. **Action**: Type "Thank you! I'll be waiting."
4. **Action**: Tap send
5. **Verify**:
   - ✅ Message appears immediately
   - ✅ Rider's message marked as read
   - ✅ Unread badge disappears

#### Step 5: Rider Receives Reply (Real-time)
1. **Action**: Switch back to rider account
2. **Expected**: See buyer's reply appear automatically
3. **Verify**:
   - ✅ Message appears without refresh
   - ✅ Notification sound/vibration (if enabled)
   - ✅ Conversation moves to top of list

---

## Test Scenario 2: Buyer → Rider Communication

### Setup
1. Use same order from Scenario 1
2. Login as buyer

### Test Steps

#### Step 1: Buyer Initiates Chat
1. **Action**: Login as buyer
2. **Navigate**: Order details → "Contact Rider" button
3. **Expected**: Opens chat with rider
4. **Verify**:
   - ✅ Rider name displays
   - ✅ Rider profile picture shows
   - ✅ "Rider" role badge appears

#### Step 2: Buyer Sends Location/Instructions
1. **Action**: Type "I'm at the blue gate, please call when you arrive"
2. **Action**: Tap send
3. **Expected**: Message sent successfully
4. **Verify**:
   - ✅ Message appears in chat
   - ✅ Timestamp shows
   - ✅ Sent indicator appears

#### Step 3: Rider Receives and Responds
1. **Action**: Switch to rider account
2. **Expected**: See new message notification
3. **Action**: Open conversation
4. **Action**: Reply "Got it! I'll call you when I'm there."
5. **Verify**:
   - ✅ Buyer's message visible
   - ✅ Reply sent successfully
   - ✅ Real-time delivery works

---

## Test Scenario 3: Rider → Seller Communication

### Setup
1. Create order with items from seller
2. Assign rider to order
3. Login as rider

### Test Steps

#### Step 1: Rider Contacts Seller for Pickup
1. **Action**: Login as rider
2. **Navigate**: Orders → Order details → "Contact Seller"
3. **Expected**: Opens chat with seller
4. **Verify**:
   - ✅ Seller name/store name displays
   - ✅ Store logo shows (if available)
   - ✅ "Seller" role badge appears

#### Step 2: Rider Asks About Pickup
1. **Action**: Type "Hi! I'm here to pick up order #123. Where should I go?"
2. **Action**: Tap send
3. **Expected**: Message sent to seller
4. **Verify**:
   - ✅ Message appears in chat
   - ✅ Timestamp displays
   - ✅ Sent indicator shows

#### Step 3: Seller Receives and Responds
1. **Action**: Login as seller
2. **Navigate**: Messages/Inbox
3. **Expected**: See rider's message
4. **Verify**:
   - ✅ Unread badge shows
   - ✅ Rider appears in conversations
   - ✅ "Rider" role badge displays
5. **Action**: Reply "Please come to the back entrance, I'll meet you there"
6. **Verify**:
   - ✅ Reply sent successfully

#### Step 4: Rider Receives Instructions
1. **Action**: Switch back to rider account
2. **Expected**: See seller's reply
3. **Verify**:
   - ✅ Message appears in real-time
   - ✅ Notification received
   - ✅ Can continue conversation

---

## Test Scenario 4: Seller → Rider Communication

### Setup
1. Use same order from Scenario 3
2. Login as seller

### Test Steps

#### Step 1: Seller Initiates Chat
1. **Action**: Login as seller
2. **Navigate**: Orders → Order details → "Contact Rider"
3. **Expected**: Opens chat with rider
4. **Verify**:
   - ✅ Rider name displays
   - ✅ Rider profile picture shows
   - ✅ "Rider" role badge appears

#### Step 2: Seller Sends Special Instructions
1. **Action**: Type "Please handle with care - fragile items inside"
2. **Action**: Tap send
3. **Expected**: Message sent to rider
4. **Verify**:
   - ✅ Message appears
   - ✅ Sent successfully

#### Step 3: Rider Acknowledges
1. **Action**: Switch to rider account
2. **Expected**: See seller's message
3. **Action**: Reply "Understood! I'll be extra careful."
4. **Verify**:
   - ✅ Real-time delivery works
   - ✅ Conversation flows naturally

---

## Test Scenario 5: Real-Time Features

### Typing Indicators

#### Test Steps
1. **Action**: Open chat between rider and buyer
2. **Action**: Start typing on rider's device
3. **Expected**: Buyer sees "Rider is typing..." indicator
4. **Verify**:
   - ✅ Typing indicator appears within 1 second
   - ✅ Animated dots show
   - ✅ Indicator disappears when typing stops

### Read Receipts

#### Test Steps
1. **Action**: Rider sends message to buyer
2. **Expected**: Single check mark (sent)
3. **Action**: Buyer opens conversation
4. **Expected**: Double check mark (read)
5. **Verify**:
   - ✅ Check marks update in real-time
   - ✅ Unread badge disappears
   - ✅ Message marked as read in database

### Online Status

#### Test Steps
1. **Action**: Open conversations list
2. **Expected**: See online/offline status for each user
3. **Verify**:
   - ✅ Green dot for online users
   - ✅ Gray dot for offline users
   - ✅ Status updates in real-time

---

## Test Scenario 6: Multiple Conversations

### Test Steps

#### Step 1: Rider with Multiple Chats
1. **Action**: Login as rider
2. **Action**: Start chat with Buyer A
3. **Action**: Start chat with Buyer B
4. **Action**: Start chat with Seller A
5. **Expected**: See all 3 conversations in list
6. **Verify**:
   - ✅ All conversations appear
   - ✅ Sorted by most recent
   - ✅ Unread counts accurate
   - ✅ Last message previews correct

#### Step 2: Switch Between Conversations
1. **Action**: Send message in each conversation
2. **Action**: Switch between conversations
3. **Expected**: Messages persist correctly
4. **Verify**:
   - ✅ No message loss
   - ✅ Correct messages in each chat
   - ✅ Scroll position maintained

---

## Test Scenario 7: Edge Cases

### Empty Conversation
1. **Action**: Open chat with no messages
2. **Expected**: See "No messages yet" state
3. **Verify**:
   - ✅ Empty state displays
   - ✅ Can send first message
   - ✅ UI updates after first message

### Long Messages
1. **Action**: Send message with 500+ characters
2. **Expected**: Message sent successfully
3. **Verify**:
   - ✅ Message displays correctly
   - ✅ Text wraps properly
   - ✅ Bubble expands to fit content

### Special Characters
1. **Action**: Send message with emojis: "👍 Great! 🚚"
2. **Expected**: Emojis display correctly
3. **Verify**:
   - ✅ Emojis render properly
   - ✅ No encoding issues

### Network Issues
1. **Action**: Turn off internet
2. **Action**: Try to send message
3. **Expected**: Error message shown
4. **Verify**:
   - ✅ User notified of failure
   - ✅ Message not lost
   - ✅ Can retry when online

### Rapid Messages
1. **Action**: Send 10 messages quickly
2. **Expected**: All messages sent
3. **Verify**:
   - ✅ All messages appear
   - ✅ Correct order maintained
   - ✅ No duplicates

---

## Test Scenario 8: Database Verification

### SQL Queries to Verify

#### Check Rider-Buyer Messages
```sql
SELECT 
    cm.id,
    cm.message,
    cm.created_at,
    sender.first_name || ' ' || sender.last_name as sender_name,
    sender.role as sender_role,
    receiver.first_name || ' ' || receiver.last_name as receiver_name,
    receiver.role as receiver_role
FROM chat_message cm
JOIN "user" sender ON cm.sender_id = sender.id
JOIN "user" receiver ON cm.receiver_id = receiver.id
WHERE (sender.role = 'rider' AND receiver.role = 'buyer')
   OR (sender.role = 'buyer' AND receiver.role = 'rider')
ORDER BY cm.created_at DESC
LIMIT 20;
```

#### Check Rider-Seller Messages
```sql
SELECT 
    cm.id,
    cm.message,
    cm.created_at,
    sender.first_name || ' ' || sender.last_name as sender_name,
    sender.role as sender_role,
    receiver.first_name || ' ' || receiver.last_name as receiver_name,
    receiver.role as receiver_role
FROM chat_message cm
JOIN "user" sender ON cm.sender_id = sender.id
JOIN "user" receiver ON cm.receiver_id = receiver.id
WHERE (sender.role = 'rider' AND receiver.role = 'seller')
   OR (sender.role = 'seller' AND receiver.role = 'rider')
ORDER BY cm.created_at DESC
LIMIT 20;
```

#### Check Unread Messages
```sql
SELECT 
    receiver.first_name || ' ' || receiver.last_name as receiver_name,
    receiver.role as receiver_role,
    COUNT(*) as unread_count
FROM chat_message cm
JOIN "user" receiver ON cm.receiver_id = receiver.id
WHERE cm.is_read = FALSE
GROUP BY receiver.id, receiver.first_name, receiver.last_name, receiver.role
ORDER BY unread_count DESC;
```

---

## Test Scenario 9: Performance Testing

### Load Test
1. **Action**: Send 100 messages in conversation
2. **Expected**: App remains responsive
3. **Verify**:
   - ✅ Smooth scrolling
   - ✅ No lag when sending
   - ✅ Messages load quickly

### Concurrent Users
1. **Action**: 3 users chatting simultaneously
2. **Expected**: All messages delivered
3. **Verify**:
   - ✅ No message loss
   - ✅ Real-time delivery works
   - ✅ No conflicts

---

## Test Scenario 10: UI/UX Verification

### Visual Elements
- ✅ Profile pictures display correctly
- ✅ Role badges show correct colors
- ✅ Timestamps formatted properly
- ✅ Message bubbles styled correctly
- ✅ Unread badges visible
- ✅ Online status indicators work

### Interactions
- ✅ Tap to open conversation
- ✅ Swipe to go back
- ✅ Pull to refresh conversations
- ✅ Keyboard appears/dismisses smoothly
- ✅ Send button enabled/disabled correctly

### Accessibility
- ✅ Text readable (font size, contrast)
- ✅ Touch targets large enough
- ✅ Screen reader compatible
- ✅ Keyboard navigation works

---

## Success Criteria

All tests pass if:
- ✅ Rider can chat with buyer
- ✅ Buyer can chat with rider
- ✅ Rider can chat with seller
- ✅ Seller can chat with rider
- ✅ Real-time messaging works
- ✅ Read receipts accurate
- ✅ Typing indicators functional
- ✅ No message loss
- ✅ Database records correct
- ✅ UI/UX smooth and responsive

---

## Troubleshooting Guide

### Issue: Messages not appearing
**Solution**: 
1. Check Socket.IO connection in logs
2. Verify access token is valid
3. Restart backend server
4. Clear app cache

### Issue: Typing indicators not working
**Solution**:
1. Check Socket.IO connection
2. Verify both users in same conversation
3. Check network connectivity

### Issue: Profile pictures not loading
**Solution**:
1. Verify image paths in database
2. Check file permissions on server
3. Ensure images uploaded correctly

### Issue: Unread counts incorrect
**Solution**:
1. Check `is_read` field in database
2. Verify mark-as-read API called
3. Refresh conversations list

---

## Conclusion

If all test scenarios pass, your unified chat system is **fully functional** for:
- ✅ Rider ↔ Buyer communication
- ✅ Rider ↔ Seller communication
- ✅ Buyer ↔ Seller communication

The system is **production-ready**! 🎉
