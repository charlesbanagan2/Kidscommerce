# Unified Chat Migration - Quick Start Guide

## 🚀 How to Complete the Migration

This guide provides step-by-step instructions to complete the unified chat migration.

---

## Step 1: Fix Database Connection (CRITICAL)

### Problem
The migration script cannot connect to the Supabase database.

### Solution
1. **Locate the environment file:**
   ```
   mobile_app/lib/kids_commercedb/supabase.env
   ```

2. **Verify these variables are correct:**
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_DB_URL=postgresql://postgres:password@db.your-project.supabase.co:6543/postgres
   SUPABASE_DB_PASSWORD=your-password
   ```

3. **Test the connection:**
   ```bash
   cd backend
   python -c "from run_unified_chat_migration import get_db_url; print(get_db_url())"
   ```

4. **If connection fails:**
   - Check if Supabase project is active
   - Verify network connectivity
   - Try connecting with `psql` directly
   - Check firewall settings

---

## Step 2: Run Data Migration

### Prerequisites
- ✅ Database connection working
- ✅ `chat_message` table exists (run `migrate_chat_standalone.py` if not)
- ✅ Backup of current database (recommended)

### Execute Migration
```bash
cd backend
python run_unified_chat_migration.py
```

### Expected Output
```
======================================================================
UNIFIED CHAT SYSTEM MIGRATION
======================================================================

📦 Creating backups of legacy tables...
  - StoreChatMessage: X records
    ✅ Backup created: backups/store_chat_message_backup_TIMESTAMP.sql
  - RiderChatMessage: Y records
    ✅ Backup created: backups/rider_chat_message_backup_TIMESTAMP.sql

📦 Migrating StoreChatMessage records...
  Total records to migrate: X
  Progress: X/X (X success, 0 errors)
  ✅ Migration complete: X success, 0 errors

📦 Migrating RiderChatMessage records...
  Total records to migrate: Y
  Progress: Y/Y (Y success, 0 errors)
  ✅ Migration complete: Y success, 0 errors

🔍 Validating data integrity...
  Legacy tables total: Z (X store + Y rider)
  Unified table total: Z
  ✅ Record count validation PASSED

======================================================================
MIGRATION SUMMARY
======================================================================
StoreChatMessage: X migrated, 0 errors
RiderChatMessage: Y migrated, 0 errors
Validation: ✅ PASSED
Backups: 2 files created

✅ MIGRATION SUCCESSFUL!
```

### If Migration Fails
1. Check error messages in console
2. Review backup files in `backend/backups/`
3. Verify database permissions
4. Check for foreign key constraint violations
5. Run migration again (it's idempotent)

---

## Step 3: Verify Unified Chat API

### Start the Flask Server
```bash
cd backend
python app.py
```

### Test Endpoints Manually

#### 1. Get Conversations
```bash
curl -X GET http://localhost:5000/api/chat/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "peer_id": 123,
      "peer_name": "John Doe",
      "peer_role": "seller",
      "peer_profile_picture": "https://...",
      "last_message": "Hello!",
      "last_message_time": "2026-05-21T10:30:00",
      "unread_count": 2
    }
  ]
}
```

#### 2. Get Messages with User
```bash
curl -X GET http://localhost:5000/api/chat/messages/123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Send Message
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": 123,
    "message": "Test message",
    "product_id": 456
  }'
```

#### 4. Get Unread Count
```bash
curl -X GET http://localhost:5000/api/chat/unread-count \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Step 4: Test SocketIO Real-Time Messaging

### Using Browser Console
```javascript
// Connect to SocketIO
const socket = io('http://localhost:5000', {
  auth: {
    token: 'YOUR_JWT_TOKEN'
  }
});

// Join chat room
socket.emit('join_chat');

// Listen for new messages
socket.on('new_message', (data) => {
  console.log('New message received:', data);
});

// Listen for typing indicators
socket.on('user_typing', (data) => {
  console.log('User is typing:', data);
});

// Send typing indicator
socket.emit('typing', { receiver_id: 123 });

// Stop typing indicator
socket.emit('stop_typing', { receiver_id: 123 });
```

### Expected Events
- `joined_chat` - Confirmation of room join
- `new_message` - New message received
- `user_typing` - Other user is typing
- `user_stop_typing` - Other user stopped typing
- `conversation_updated` - Conversation list needs update
- `unread_cleared` - Unread count cleared

---

## Step 5: Test Mobile App Integration

### Prerequisites
- Mobile app running (iOS/Android)
- Backend server running
- JWT authentication working

### Test Checklist
- [ ] Login to mobile app
- [ ] Navigate to Messages/Chat screen
- [ ] Verify conversation list loads
- [ ] Open a conversation
- [ ] Send a message
- [ ] Verify message appears in chat
- [ ] Verify real-time message delivery
- [ ] Check unread count badge
- [ ] Test mark-as-read functionality
- [ ] Test typing indicators
- [ ] Test product chat (from product page)
- [ ] Test order chat (from order details)

### Common Issues
1. **Conversation list not updating:**
   - Check SocketIO connection
   - Verify `conversation_updated` event is emitted
   - Check mobile app event listeners

2. **Messages not appearing:**
   - Check API response
   - Verify message sorting (ascending by created_at)
   - Check for duplicate message prevention logic

3. **Scroll not working:**
   - Verify `_scrollToBottom()` is called after messages load
   - Check scroll animation settings

---

## Step 6: Test Seller Inbox

### Access Seller Dashboard
1. Login as seller user
2. Navigate to Messages/Inbox
3. Verify conversation list displays

### Test Checklist
- [ ] Conversation list shows all buyer conversations
- [ ] Unread indicators display correctly
- [ ] Product context shows in conversations
- [ ] Can send messages to buyers
- [ ] Real-time updates work
- [ ] Mark-as-read works when viewing conversation
- [ ] Profile photos display correctly
- [ ] Can filter conversations by product

---

## Step 7: Monitor and Validate

### Check Application Logs
```bash
# View Flask logs
tail -f backend/logs/app.log

# Check for errors
grep ERROR backend/logs/app.log

# Check chat-related logs
grep "chat" backend/logs/app.log
```

### Monitor Database
```sql
-- Check record counts
SELECT COUNT(*) FROM chat_message;
SELECT COUNT(*) FROM store_chat_message;
SELECT COUNT(*) FROM rider_chat_message;

-- Check recent messages
SELECT * FROM chat_message ORDER BY created_at DESC LIMIT 10;

-- Check unread messages
SELECT COUNT(*) FROM chat_message WHERE is_read = false;

-- Check messages by user
SELECT sender_id, receiver_id, COUNT(*) 
FROM chat_message 
GROUP BY sender_id, receiver_id;
```

### Performance Metrics
- API response time < 500ms
- SocketIO latency < 100ms
- Database query time < 200ms
- Message delivery time < 1 second

---

## Step 8: Clean Up Legacy Code (After 48 Hours)

### Only After Confirming Everything Works!

1. **Drop legacy tables (CAREFUL!):**
   ```sql
   -- Create final backup first!
   DROP TABLE IF EXISTS store_chat_message;
   DROP TABLE IF EXISTS rider_chat_message;
   ```

2. **Remove legacy model comments from app.py:**
   - Search for "Legacy chat models removed"
   - Remove comment blocks if desired

3. **Archive backup files:**
   ```bash
   mkdir backend/backups/archive
   mv backend/backups/*.sql backend/backups/archive/
   ```

---

## 🆘 Troubleshooting

### Issue: Migration Script Fails
**Solution:**
1. Check database connection
2. Verify table exists: `SELECT * FROM chat_message LIMIT 1;`
3. Check for foreign key violations
4. Review error logs
5. Run with smaller batch size: Edit `batch_size=100` in script

### Issue: API Returns 401 Unauthorized
**Solution:**
1. Verify JWT token is valid
2. Check `JWT_SECRET_KEY` in environment
3. Verify token is in `Authorization: Bearer TOKEN` format
4. Check token expiration

### Issue: SocketIO Not Connecting
**Solution:**
1. Verify Flask-SocketIO is installed
2. Check CORS settings
3. Verify client is using correct URL
4. Check firewall/network settings
5. Review browser console for errors

### Issue: Messages Not Appearing
**Solution:**
1. Check API response: `console.log(response)`
2. Verify database has messages: `SELECT * FROM chat_message`
3. Check message sorting order
4. Verify sender_id and receiver_id are correct
5. Check for JavaScript errors in console

### Issue: Real-Time Updates Not Working
**Solution:**
1. Verify SocketIO connection: `socket.connected`
2. Check event listeners are registered
3. Verify room join: `socket.emit('join_chat')`
4. Check server logs for emit errors
5. Test with multiple browser tabs

---

## 📊 Success Checklist

Before considering migration complete, verify:

- [ ] Data migration completed with 100% success rate
- [ ] All API endpoints return correct responses
- [ ] SocketIO real-time messaging works
- [ ] Mobile app chat functions correctly
- [ ] Seller inbox displays conversations
- [ ] Buyer-seller chat works (with product context)
- [ ] Buyer-rider chat works (with order context)
- [ ] Unread counts are accurate
- [ ] Mark-as-read functionality works
- [ ] Typing indicators work
- [ ] Profile photos display correctly
- [ ] No errors in application logs for 24 hours
- [ ] Performance meets requirements
- [ ] All user roles tested (buyer, seller, rider)
- [ ] All platforms tested (web, mobile iOS, mobile Android)

---

## 📞 Need Help?

1. **Check migration status:** Review `MIGRATION_STATUS.md`
2. **Review logs:** Check `backend/logs/` directory
3. **Test manually:** Use curl commands above
4. **Check database:** Run SQL queries above
5. **Review code:** Check `unified_chat_api.py` for implementation

---

**Good luck with the migration! 🚀**
