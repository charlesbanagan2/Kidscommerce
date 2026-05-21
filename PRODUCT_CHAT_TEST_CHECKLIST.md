# Product Chat - Testing Checklist ✅

## Pre-Testing Setup

### 1. Start Backend
```bash
cd backend
python app.py
```
**Expected:** Server starts on port 5000, no errors

### 2. Start Mobile App
```bash
cd mobile_app
flutter run
```
**Expected:** App builds and runs successfully

---

## Test Scenario 1: Send Product Message (BUYER)

### Steps:
1. [ ] Login as BUYER
2. [ ] Navigate to any product detail page
3. [ ] Click the message icon (💬) at bottom
4. [ ] Type a test message: "Available pa ba ito?"
5. [ ] Click send button

### Expected Results:
- [ ] ✅ Message appears immediately in chat screen
- [ ] ✅ No loading spinner stuck
- [ ] ✅ Message shows with correct timestamp
- [ ] ✅ Product card shows at top (image, name, price)
- [ ] ✅ Seller's avatar/name shows correctly

### Debug Console Check:
```
📤 Send message response: {success: true, message: {...}}
```

---

## Test Scenario 2: View in Messages Tab (BUYER)

### Steps:
1. [ ] After sending message, press back button
2. [ ] Go to Home screen
3. [ ] Click Messages tab (bottom navigation)
4. [ ] Look for the conversation

### Expected Results:
- [ ] ✅ Product conversation appears in list
- [ ] ✅ Shows "📦 [Product Name]: [Last Message]"
- [ ] ✅ Shows seller's name and avatar
- [ ] ✅ Shows "Seller" role badge
- [ ] ✅ Shows timestamp
- [ ] ✅ Shows unread count badge (if unread)

### Click the Conversation:
- [ ] ✅ Opens ProductChatScreen
- [ ] ✅ Shows product card at top
- [ ] ✅ Shows all messages
- [ ] ✅ Can send new messages

---

## Test Scenario 3: Seller Dashboard (SELLER)

### Steps:
1. [ ] Open web browser
2. [ ] Login as SELLER
3. [ ] Navigate to dashboard

### Expected Results:
- [ ] ✅ Dashboard loads without errors
- [ ] ✅ No "StoreChatMessage" error in console
- [ ] ✅ Unread chat count shows correctly
- [ ] ✅ Can navigate to orders page
- [ ] ✅ Can view order details

### Backend Console Check:
```
No errors about StoreChatMessage
```

---

## Test Scenario 4: Multiple Product Chats (BUYER)

### Steps:
1. [ ] Send message to Product A
2. [ ] Go back, find Product B
3. [ ] Send message to Product B
4. [ ] Go to Messages tab

### Expected Results:
- [ ] ✅ Both conversations appear
- [ ] ✅ Sorted by latest message (newest first)
- [ ] ✅ Each shows correct product name
- [ ] ✅ Each shows correct seller
- [ ] ✅ Can open each conversation separately

---

## Test Scenario 5: Seller Receives Message (SELLER)

### Steps:
1. [ ] Buyer sends product message
2. [ ] Seller refreshes dashboard
3. [ ] Check unread count

### Expected Results:
- [ ] ✅ Unread count increases
- [ ] ✅ No errors in backend console
- [ ] ✅ Seller can see message (if chat UI exists)

---

## Test Scenario 6: Back and Forth Chat

### Steps:
1. [ ] Buyer sends: "Available pa ba?"
2. [ ] Seller replies: "Yes, available pa"
3. [ ] Buyer sends: "Magkano shipping?"
4. [ ] Check both sides

### Expected Results:
- [ ] ✅ All messages appear in correct order
- [ ] ✅ Buyer messages on right (blue)
- [ ] ✅ Seller messages on left (white)
- [ ] ✅ Timestamps show correctly
- [ ] ✅ Avatars show correctly

---

## Error Scenarios to Test

### Test: Send Empty Message
1. [ ] Try to send empty message
2. [ ] **Expected:** Button disabled or no action

### Test: Network Error
1. [ ] Turn off backend
2. [ ] Try to send message
3. [ ] **Expected:** Error message shows

### Test: Invalid Product
1. [ ] Try to open chat for deleted product
2. [ ] **Expected:** Graceful error handling

---

## Database Verification

### Check Messages Table:
```sql
SELECT 
  id, 
  sender_id, 
  receiver_id, 
  message, 
  product_id, 
  is_read,
  created_at 
FROM chat_message 
WHERE product_id IS NOT NULL 
ORDER BY created_at DESC 
LIMIT 10;
```

**Expected:** Messages with product_id populated

### Check Unread Count:
```sql
SELECT COUNT(*) 
FROM chat_message 
WHERE receiver_id = [SELLER_ID] 
AND is_read = FALSE 
AND product_id IS NOT NULL;
```

**Expected:** Correct count of unread messages

---

## Performance Checks

### Load Time:
- [ ] Product chat screen loads < 1 second
- [ ] Messages tab loads < 2 seconds
- [ ] Sending message completes < 1 second

### Memory:
- [ ] No memory leaks when opening/closing chats
- [ ] App remains responsive

### Network:
- [ ] API calls complete successfully
- [ ] No unnecessary duplicate requests

---

## Edge Cases

### Test: Very Long Message
1. [ ] Send message with 500+ characters
2. [ ] **Expected:** Message wraps correctly, no overflow

### Test: Special Characters
1. [ ] Send message with emojis: "😊 Available ba? 🎉"
2. [ ] **Expected:** Displays correctly

### Test: Rapid Messages
1. [ ] Send 5 messages quickly
2. [ ] **Expected:** All appear in order, no duplicates

### Test: Product with Long Name
1. [ ] Chat about product with 100+ character name
2. [ ] **Expected:** Name truncates gracefully in list

---

## Regression Tests

### Verify Other Features Still Work:
- [ ] Regular rider-buyer chat still works
- [ ] Order chat still works
- [ ] Notifications still work
- [ ] Cart still works
- [ ] Checkout still works

---

## Sign-Off Checklist

### Backend:
- [ ] ✅ No StoreChatMessage errors
- [ ] ✅ All 3 seller dashboard routes work
- [ ] ✅ Product chat API endpoints work
- [ ] ✅ Database queries optimized

### Mobile App:
- [ ] ✅ Product chat screen works
- [ ] ✅ Messages tab shows product chats
- [ ] ✅ Navigation works correctly
- [ ] ✅ UI looks good (no overflow, proper spacing)

### Integration:
- [ ] ✅ Backend + Mobile work together
- [ ] ✅ Real-time updates work (if implemented)
- [ ] ✅ Error handling works
- [ ] ✅ Loading states work

---

## Final Verification

### Code Quality:
- [ ] No console errors
- [ ] No warnings in Flutter
- [ ] No Python exceptions
- [ ] Code follows project conventions

### Documentation:
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Comments added where needed

### Deployment Ready:
- [ ] All tests pass
- [ ] No known bugs
- [ ] Performance acceptable
- [ ] Ready for production

---

## Test Results Summary

**Date Tested:** _________________  
**Tested By:** _________________  
**Environment:** _________________

**Overall Status:** 
- [ ] ✅ PASS - All tests successful
- [ ] ⚠️ PARTIAL - Some issues found
- [ ] ❌ FAIL - Major issues found

**Notes:**
```
[Add any observations, issues, or recommendations here]
```

---

## Quick Debug Commands

### Check Backend Logs:
```bash
# In backend terminal, look for:
[OK] Product chat API registered
[ERROR] messages (should be none)
```

### Check Flutter Logs:
```bash
# In Flutter debug console, look for:
📤 Send message response: {success: true}
❌ Error messages (should be none)
```

### Check Database:
```sql
-- Count product messages:
SELECT COUNT(*) FROM chat_message WHERE product_id IS NOT NULL;

-- Recent messages:
SELECT * FROM chat_message ORDER BY created_at DESC LIMIT 5;
```

---

**STATUS: READY FOR TESTING ✅**  
**FIXES APPLIED: May 21, 2026**
