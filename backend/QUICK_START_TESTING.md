===========================================
🚀 QUICK START GUIDE - SELLER INBOX FIX
===========================================

STEP 1: VERIFY DATABASE
------------------------
Run this SQL to check if chat_message table exists:

```sql
SELECT * FROM chat_message LIMIT 1;
```

If error, run: setup_chat_message_table.sql

STEP 2: RESTART SERVER
----------------------
```bash
cd c:\Users\mnban\Documents\kids\backend
python app.py
```

Or:
```bash
START_SERVER.bat
```

STEP 3: TEST AS BUYER
----------------------
1. Open browser: http://localhost:5000
2. Login as buyer (any buyer account)
3. Go to any product page
4. Click "Chat with Seller" or "Message Seller"
5. Type message: "Hi! I'm interested in this product"
6. Click Send
7. ✅ Message should send successfully

STEP 4: TEST AS SELLER
-----------------------
1. Open new browser tab (or incognito)
2. Login as seller (the product's seller)
3. Go to: http://localhost:5000/seller/inbox
4. ✅ You should see the buyer in the list
5. ✅ Should show unread count badge
6. Click on the buyer
7. ✅ Should see the message
8. ✅ Should see product info (if product chat)
9. Type reply: "Hello! Yes, this product is available"
10. Click Send
11. ✅ Reply should send successfully

STEP 5: VERIFY BUYER RECEIVES REPLY
------------------------------------
1. Go back to buyer browser tab
2. Refresh or check messages
3. ✅ Should see seller's reply
4. ✅ Can continue conversation

TROUBLESHOOTING
---------------

Problem: Seller inbox is empty
Solution:
- Check database: SELECT * FROM chat_message;
- Check if buyer sent message
- Check seller_id matches product seller

Problem: Messages not saving
Solution:
- Check server logs for errors
- Verify chat_message table exists
- Check database connection

Problem: No real-time updates
Solution:
- Check Socket.IO connection
- Verify socketio is running
- Check browser console for errors

Problem: Product info not showing
Solution:
- Verify product_id is set in message
- Check product exists in database
- Check LEFT JOIN in SQL query

QUICK DATABASE CHECKS
---------------------

1. Check all messages:
```sql
SELECT 
    cm.id,
    u1.first_name || ' ' || u1.last_name as sender,
    u2.first_name || ' ' || u2.last_name as receiver,
    cm.message,
    cm.created_at
FROM chat_message cm
JOIN "user" u1 ON cm.sender_id = u1.id
JOIN "user" u2 ON cm.receiver_id = u2.id
ORDER BY cm.created_at DESC
LIMIT 10;
```

2. Check unread messages:
```sql
SELECT 
    u.first_name || ' ' || u.last_name as receiver,
    COUNT(*) as unread
FROM chat_message cm
JOIN "user" u ON cm.receiver_id = u.id
WHERE cm.is_read = FALSE
GROUP BY u.id, u.first_name, u.last_name;
```

3. Check specific conversation:
```sql
SELECT * FROM chat_message
WHERE (sender_id = [buyer_id] AND receiver_id = [seller_id])
   OR (sender_id = [seller_id] AND receiver_id = [buyer_id])
ORDER BY created_at ASC;
```

EXPECTED RESULTS
----------------

✅ Buyer can send messages
✅ Messages save to chat_message table
✅ Seller sees messages in inbox
✅ Seller sees unread count
✅ Seller can reply
✅ Buyer receives replies
✅ Product info displays correctly
✅ Timestamps show correctly
✅ Real-time updates work

FILES TO CHECK
--------------

1. Backend:
   - app.py (lines 12239, 13210)
   - unified_chat_api.py
   - product_chat_api.py

2. Database:
   - chat_message table
   - Indexes on chat_message

3. Frontend:
   - seller/inbox.html
   - buyer/messages.html

SUPPORT
-------

If still having issues:

1. Check server logs:
   - Look for [ERROR] messages
   - Check stack traces

2. Check database:
   - Verify table structure
   - Check for messages
   - Verify indexes

3. Check browser console:
   - Look for JavaScript errors
   - Check Socket.IO connection
   - Verify API calls

4. Test API directly:
   ```bash
   curl -X POST http://localhost:5000/api/v1/chat/send \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer [token]" \
     -d '{"receiver_id": 2, "message": "Test"}'
   ```

SUCCESS INDICATORS
------------------

✅ No errors in server logs
✅ Messages appear in database
✅ Seller inbox shows buyers
✅ Unread count is accurate
✅ Messages display correctly
✅ Replies work both ways
✅ Product info shows when applicable
✅ Real-time updates work

===========================================
READY TO TEST! GOOD LUCK! 🎉
===========================================
