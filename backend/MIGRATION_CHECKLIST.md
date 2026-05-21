# Unified Chat Migration - Execution Checklist

**Use this checklist to track migration progress step-by-step.**

---

## Pre-Migration Checklist

### Database Preparation
- [ ] Verify Supabase project is active
- [ ] Test database connection manually
- [ ] Confirm `chat_message` table exists
- [ ] Create manual database backup (recommended)
- [ ] Stop Flask server if running

### Environment Verification
- [ ] Check `mobile_app/lib/kids_commercedb/supabase.env` exists
- [ ] Verify `SUPABASE_URL` is correct
- [ ] Verify `SUPABASE_DB_URL` or connection components are correct
- [ ] Test connection: `python -c "from run_unified_chat_migration import get_db_url; print(get_db_url())"`

### Code Verification
- [ ] Confirm `backend/unified_chat_api.py` exists
- [ ] Confirm `backend/run_unified_chat_migration.py` exists
- [ ] Verify legacy routes removed from `backend/app.py` (lines 7695-8002)

---

## Migration Execution

### Step 1: Run Migration Script
```bash
cd backend
python run_unified_chat_migration.py
```

- [ ] Script starts without errors
- [ ] Backup files created in `backend/backups/`
- [ ] StoreChatMessage migration completes
- [ ] RiderChatMessage migration completes
- [ ] Validation passes (record counts match)
- [ ] No critical errors in output

### Step 2: Review Migration Output
- [ ] Note total records migrated: ___________
- [ ] Note any error count: ___________
- [ ] Validation status: PASSED / FAILED
- [ ] Backup file locations recorded

---

## Post-Migration Testing

### Step 3: Start Flask Server
```bash
cd backend
python app.py
```

- [ ] Server starts without errors
- [ ] No import errors for ChatMessage model
- [ ] Unified chat API registered successfully
- [ ] SocketIO initialized

### Step 4: Test REST API Endpoints

#### Get Conversations
```bash
curl -X GET http://localhost:5000/api/chat/conversations \
  -H "Authorization: Bearer YOUR_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Returns conversation list
- [ ] Shows correct unread counts

#### Get Messages
```bash
curl -X GET http://localhost:5000/api/chat/messages/USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Returns message list
- [ ] Messages ordered by created_at ascending

#### Send Message
```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_id": USER_ID, "message": "Test"}'
```
- [ ] Returns 201 Created
- [ ] Message saved to database
- [ ] SocketIO event emitted

#### Mark as Read
```bash
curl -X POST http://localhost:5000/api/chat/mark-read/USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Messages marked as read in database

#### Get Unread Count
```bash
curl -X GET http://localhost:5000/api/chat/unread-count \
  -H "Authorization: Bearer YOUR_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Shows correct unread count

### Step 5: Test SocketIO Events

Open browser console and run:
```javascript
const socket = io('http://localhost:5000', {
  auth: { token: 'YOUR_TOKEN' }
});
socket.emit('join_chat');
socket.on('joined_chat', (data) => console.log('Joined:', data));
socket.on('new_message', (data) => console.log('New message:', data));
```

- [ ] Socket connects successfully
- [ ] `joined_chat` event received
- [ ] Can send messages via API and receive `new_message` event
- [ ] Typing indicators work
- [ ] `conversation_updated` event received

---

## User Acceptance Testing

### Buyer-Seller Chat
- [ ] Buyer can see seller conversations
- [ ] Buyer can send message to seller
- [ ] Seller receives message in real-time
- [ ] Seller can reply to buyer
- [ ] Buyer receives reply in real-time
- [ ] Unread count updates correctly
- [ ] Mark-as-read works when viewing conversation
- [ ] Product context displays (if applicable)

### Buyer-Rider Chat
- [ ] Buyer can see rider conversations
- [ ] Buyer can send message to rider
- [ ] Rider receives message in real-time
- [ ] Rider can reply to buyer
- [ ] Buyer receives reply in real-time
- [ ] Unread count updates correctly
- [ ] Mark-as-read works when viewing conversation
- [ ] Order context displays (if applicable)

### Seller Inbox
- [ ] Seller can access inbox/messages page
- [ ] All buyer conversations display
- [ ] Unread indicators show correctly
- [ ] Can click conversation to view messages
- [ ] Can send reply to buyer
- [ ] Real-time updates work
- [ ] Profile photos display
- [ ] Product context shows

---

## Mobile App Testing

### iOS App
- [ ] Login successful
- [ ] Navigate to Messages screen
- [ ] Conversation list loads
- [ ] Can open conversation
- [ ] Can send message
- [ ] Message appears in chat
- [ ] Real-time message delivery works
- [ ] Unread badge updates
- [ ] Typing indicators work
- [ ] Scroll to bottom works
- [ ] No duplicate messages

### Android App
- [ ] Login successful
- [ ] Navigate to Messages screen
- [ ] Conversation list loads
- [ ] Can open conversation
- [ ] Can send message
- [ ] Message appears in chat
- [ ] Real-time message delivery works
- [ ] Unread badge updates
- [ ] Typing indicators work
- [ ] Scroll to bottom works
- [ ] No duplicate messages

---

## Performance Testing

### Response Times
- [ ] GET /api/chat/conversations < 500ms
- [ ] GET /api/chat/messages < 500ms
- [ ] POST /api/chat/send < 200ms
- [ ] SocketIO message delivery < 1s

### Load Testing (Optional)
- [ ] Test with 10 concurrent users
- [ ] Test with 50 concurrent users
- [ ] Test with 100 concurrent users
- [ ] No errors under load
- [ ] Response times acceptable under load

---

## Monitoring (First 48 Hours)

### Hour 1
- [ ] Check application logs for errors
- [ ] Monitor database performance
- [ ] Verify no user complaints
- [ ] Check SocketIO connection count

### Hour 6
- [ ] Review error logs
- [ ] Check message delivery success rate
- [ ] Verify unread counts are accurate
- [ ] Monitor server resource usage

### Hour 24
- [ ] Full log review
- [ ] Database query performance check
- [ ] User feedback review
- [ ] Any issues reported?

### Hour 48
- [ ] Final log review
- [ ] Confirm no critical errors
- [ ] Verify all features working
- [ ] Decision: Proceed with cleanup or rollback?

---

## Post-Migration Cleanup (After 48 Hours)

### Database Cleanup (CAREFUL!)
- [ ] Confirm migration successful for 48+ hours
- [ ] Create final backup of legacy tables
- [ ] Document backup location: ___________
- [ ] Drop legacy tables:
  ```sql
  DROP TABLE IF EXISTS store_chat_message;
  DROP TABLE IF EXISTS rider_chat_message;
  ```
- [ ] Verify application still works after drop

### Code Cleanup
- [ ] Remove legacy model comments from app.py (optional)
- [ ] Archive migration scripts
- [ ] Update documentation

### Archive Backups
- [ ] Move backup files to archive directory
- [ ] Document retention policy (recommend 30 days)
- [ ] Set reminder to delete old backups

---

## Rollback Procedure (If Needed)

### When to Rollback
- Data validation fails
- Critical functionality broken
- More than 5% of messages lost
- Performance degraded significantly
- User complaints about missing messages

### Rollback Steps
1. [ ] Stop Flask server
2. [ ] Restore legacy tables from backup:
   ```bash
   psql $DATABASE_URL < backups/store_chat_message_backup_TIMESTAMP.sql
   psql $DATABASE_URL < backups/rider_chat_message_backup_TIMESTAMP.sql
   ```
3. [ ] Clear chat_message table:
   ```sql
   TRUNCATE TABLE chat_message;
   ```
4. [ ] Restore legacy routes in app.py (from git history)
5. [ ] Restart Flask server
6. [ ] Verify legacy system works
7. [ ] Investigate migration failure
8. [ ] Fix issues and retry migration

---

## Sign-Off

### Migration Completed By
- Name: ___________________________
- Date: ___________________________
- Time: ___________________________

### Migration Verified By
- Name: ___________________________
- Date: ___________________________
- Time: ___________________________

### Issues Encountered
- Issue 1: ___________________________
- Resolution: ___________________________
- Issue 2: ___________________________
- Resolution: ___________________________

### Final Status
- [ ] Migration SUCCESSFUL - All tests passed
- [ ] Migration PARTIAL - Some issues remain
- [ ] Migration FAILED - Rollback performed

### Notes
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________

---

**Migration Complete! 🎉**
