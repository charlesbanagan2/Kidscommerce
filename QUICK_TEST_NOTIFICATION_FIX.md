# Quick Test Guide - Notification API Fix

## 🚀 Quick Start

### 1. Restart Backend (REQUIRED)
```bash
cd backend
python app.py
```

**Look for this message in console:**
```
[OK] Notification API initialized
```

If you see an error instead, the fix didn't work properly.

### 2. Test from Mobile App

#### Test 1: Open Notifications Screen
1. Login to the app
2. Tap on the notifications icon
3. **Expected**: Notifications load successfully
4. **Before Fix**: 500 error with SQLAlchemy message

#### Test 2: Check Unread Count
1. Look at the notification badge
2. **Expected**: Shows correct number of unread notifications
3. **Before Fix**: May show 0 or error

#### Test 3: Mark as Read
1. Tap on an unread notification
2. **Expected**: Notification turns to "read" state
3. **Expected**: Unread count decreases by 1

#### Test 4: Mark All as Read
1. Tap "Mark all read" button
2. **Expected**: All notifications marked as read
3. **Expected**: Unread count becomes 0

## 🔍 Troubleshooting

### Error: "Notification system not properly initialized"
**Cause**: The notification API wasn't registered correctly
**Fix**: 
1. Check that `register_notification_api(app, db, Notification, User)` is called in app.py
2. Ensure it's called AFTER the Notification model is defined
3. Restart the backend server

### Error: Still getting 500 errors
**Cause**: Database connection or model issues
**Fix**:
1. Check database connection is working
2. Verify notification table exists: `SELECT * FROM notification LIMIT 1;`
3. Check backend console for detailed error messages

### Error: "Token is missing" or "Token is invalid"
**Cause**: Authentication issue
**Fix**:
1. Logout and login again in the mobile app
2. Check JWT_SECRET_KEY is set in backend .env file
3. Verify token is being sent in Authorization header

## 📊 Expected API Responses

### GET /api/v1/notifications
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "title": "Order Placed",
      "message": "Your order #123 has been placed",
      "type": "order",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00",
      "order_id": 123
    }
  ],
  "total_count": 10,
  "unread_count": 5,
  "has_more": false
}
```

### GET /api/v1/notifications/unread-count
```json
{
  "success": true,
  "unread_count": 5
}
```

### PUT /api/v1/notifications/123/read
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

## ✅ Success Indicators

- ✅ Backend starts without errors
- ✅ Console shows "[OK] Notification API initialized"
- ✅ Mobile app loads notifications without 500 error
- ✅ Unread count displays correctly
- ✅ Mark as read functionality works
- ✅ No SQLAlchemy errors in backend logs

## 🐛 Common Issues

### Issue: Notifications not showing
**Check**:
1. Are there notifications in the database for this user?
2. Is the user_id correct in the JWT token?
3. Check backend logs for SQL queries

### Issue: Unread count always 0
**Check**:
1. Are notifications marked as is_read=false in database?
2. Check the query in backend logs
3. Verify user_id matches

### Issue: Can't mark as read
**Check**:
1. Is the notification_id correct?
2. Does the notification belong to the current user?
3. Check backend logs for database errors

## 📝 Testing Checklist

- [ ] Backend starts successfully
- [ ] No errors in backend console
- [ ] Mobile app can fetch notifications
- [ ] Unread count is correct
- [ ] Can mark individual notification as read
- [ ] Can mark all notifications as read
- [ ] Can delete notifications
- [ ] Pagination works (if more than 20 notifications)
- [ ] Filter by type works (orders, promos, etc.)
- [ ] Real-time updates work (if implemented)

## 🎯 Quick Commands

### Check Backend Status
```bash
# Windows
curl http://localhost:5000/api/v1/notifications/unread-count -H "Authorization: Bearer YOUR_TOKEN"

# PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/notifications/unread-count" -Headers @{"Authorization"="Bearer YOUR_TOKEN"}
```

### Check Database
```sql
-- Count total notifications
SELECT COUNT(*) FROM notification;

-- Count unread notifications for user
SELECT COUNT(*) FROM notification WHERE user_id = 1 AND is_read = false;

-- View recent notifications
SELECT id, user_id, title, message, is_read, created_at 
FROM notification 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🔧 If All Else Fails

1. **Check the error message carefully** - It will tell you what's wrong
2. **Look at backend console** - Full stack traces are printed there
3. **Verify database schema** - Make sure notification table has all required columns
4. **Check JWT token** - Make sure it's valid and not expired
5. **Restart everything** - Backend server AND mobile app

## 📞 Need Help?

If you're still having issues:
1. Copy the exact error message from backend console
2. Copy the API response from mobile app logs
3. Check the NOTIFICATION_API_FIX_COMPLETE.md for detailed information

---

**Status**: ✅ All fixes applied and ready for testing
**Last Updated**: 2024
