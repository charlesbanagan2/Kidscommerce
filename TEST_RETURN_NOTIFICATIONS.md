# Test Return/Refund Notifications - Quick Guide

## Status: FIXES ALREADY APPLIED ✅

All notification fixes have been implemented. Follow this guide to test if they're working.

---

## Test 1: Buyer Requests Return → Seller Gets Notification

### Steps:
1. **Login as BUYER**
2. Go to "My Orders" → "Completed" tab
3. Find a completed order
4. Click order to view details
5. Click "Request Return/Refund" button
6. Fill out form:
   - Reason: "Wrong item received"
   - Description: "I received a different product"
   - Upload 1-2 photos
7. Click "Submit Request"

### Expected Results:
✅ Buyer sees success message  
✅ **SELLER receives notification immediately**

### Check Seller Notification:
1. Login as SELLER (in another browser/tab)
2. Look at notification bell icon (top right)
3. **Should show:** Red badge with unread count
4. Click notification bell
5. **Should see:** "Return/Refund Request" notification
6. **Message:** "Buyer requested return/refund for Order #123 — Product Name. Reason: Wrong item received"
7. Click notification → Should go to return detail page

### Debug if Not Working:
```bash
# Check backend console for:
Error sending seller notification: ...

# Check database:
SELECT * FROM notification 
WHERE message LIKE '%Return/Refund Request%' 
ORDER BY created_at DESC LIMIT 5;
```

---

## Test 2: Seller Rejects Return → Buyer Gets Notification

### Steps:
1. **Login as SELLER**
2. Go to "Returns" section (sidebar)
3. Find the pending return request
4. Click "View Details"
5. Click "Reject" button
6. Enter reason: "Item shows signs of use"
7. Click "Confirm Reject"

### Expected Results:
✅ Seller sees success message  
✅ **BUYER receives notification immediately**

### Check Buyer Notification:
1. Login as BUYER (in another browser/tab)
2. Look at notification bell icon
3. **Should show:** Red badge with unread count
4. Click notification bell
5. **Should see:** "Return Request Rejected" notification
6. **Message:** "Your return request RR-123 for Order #456 was rejected. Reason: Item shows signs of use"
7. Click notification → Should go to order detail page

### Debug if Not Working:
```bash
# Check backend console for:
Error sending rejection notification: ...

# Check database:
SELECT * FROM notification 
WHERE message LIKE '%rejected%' 
ORDER BY created_at DESC LIMIT 5;
```

---

## Test 3: Seller Approves Return → Buyer Gets Notification

### Steps:
1. **Login as SELLER**
2. Go to "Returns" section
3. Find pending return request
4. Click "View Details"
5. Click "Approve" button
6. Confirm approval

### Expected Results:
✅ Seller sees success message  
✅ **BUYER receives notification immediately**

### Check Buyer Notification:
1. Login as BUYER
2. Look at notification bell icon
3. **Should show:** Red badge with unread count
4. Click notification bell
5. **Should see:** "Return Approved & Refunded" notification
6. **Message:** "Your return request RR-123 has been approved. ₱500.00 has been refunded to your wallet."
7. Click notification → Should go to wallet page

---

## Quick Database Checks

### Check if Notifications Are Being Created:
```sql
-- Recent return/refund notifications
SELECT 
    n.id,
    n.user_id,
    u.first_name,
    u.last_name,
    u.role,
    n.title,
    n.message,
    n.is_read,
    n.created_at
FROM notification n
JOIN user u ON n.user_id = u.id
WHERE n.title LIKE '%Return%' OR n.message LIKE '%return%'
ORDER BY n.created_at DESC
LIMIT 10;
```

### Check Seller's Unread Notifications:
```sql
SELECT * FROM notification 
WHERE user_id = [SELLER_ID] 
AND is_read = FALSE 
AND (title LIKE '%Return%' OR message LIKE '%return%')
ORDER BY created_at DESC;
```

### Check Buyer's Unread Notifications:
```sql
SELECT * FROM notification 
WHERE user_id = [BUYER_ID] 
AND is_read = FALSE 
AND (title LIKE '%Reject%' OR title LIKE '%Approv%')
ORDER BY created_at DESC;
```

---

## Common Issues & Solutions

### Issue 1: No Notifications Appearing

**Possible Causes:**
1. Backend not restarted after fix
2. `create_notification` function error
3. Database connection issue

**Solution:**
```bash
# Restart backend
cd backend
# Press Ctrl+C to stop
python app.py

# Check console for errors
# Look for: "Error sending seller notification: ..."
```

### Issue 2: Notification Created But Not Showing in UI

**Check:**
1. Browser cache - Clear and refresh (Ctrl+F5)
2. Socket.IO connection - Check browser console
3. Notification bell component - Check for JavaScript errors

**Solution:**
```bash
# Clear browser cache
Ctrl + Shift + Delete

# Hard refresh
Ctrl + F5

# Check browser console (F12)
# Look for errors related to notifications
```

### Issue 3: Notification Shows But Wrong Message

**Check:**
```sql
-- Verify notification content
SELECT id, title, message, created_at 
FROM notification 
WHERE id = [NOTIFICATION_ID];
```

**Fix:**
- Check if `rr.seller_response_reason` is being saved correctly
- Verify `order.id` and `rr.id` are correct

---

## Backend Console Logs to Watch For

### Success Logs:
```
[OK] Notification created
Notification sent to user 123
```

### Error Logs:
```
Error sending seller notification: ...
Error sending rejection notification: ...
Error sending approval notification: ...
```

---

## Test Checklist

### Return Request Notification (Buyer → Seller):
- [ ] Buyer submits return request
- [ ] Seller receives notification
- [ ] Notification bell shows badge
- [ ] Notification appears in list
- [ ] Click notification goes to return detail
- [ ] Notification message is correct

### Return Rejection Notification (Seller → Buyer):
- [ ] Seller rejects return
- [ ] Buyer receives notification
- [ ] Notification bell shows badge
- [ ] Notification appears in list
- [ ] Click notification goes to order detail
- [ ] Rejection reason shows in message

### Return Approval Notification (Seller → Buyer):
- [ ] Seller approves return
- [ ] Buyer receives notification
- [ ] Notification bell shows badge
- [ ] Notification appears in list
- [ ] Click notification goes to wallet
- [ ] Refund amount shows in message

---

## Real-time Testing (Socket.IO)

### Setup:
1. Open 2 browsers side-by-side
2. Browser 1: Login as BUYER
3. Browser 2: Login as SELLER

### Test:
1. Browser 1 (Buyer): Submit return request
2. **Watch Browser 2 (Seller):**
   - Notification bell badge should update automatically
   - No page refresh needed
   - Real-time Socket.IO update

---

## Files That Were Fixed

1. ✅ `backend/app.py` (line ~14060) - Return request notification
2. ✅ `backend/app.py` (line ~14254) - Return approval notification  
3. ✅ `backend/app.py` (line ~14290) - Return rejection notification

---

## Summary

**Status:** All fixes applied ✅  
**Functions Fixed:** 3 notification functions  
**Notification System:** Using `shopee_notification_system.py`  

**What Was Fixed:**
1. Return request → Seller notification ✅
2. Return rejection → Buyer notification ✅
3. Return approval → Buyer notification ✅

**Documentation:**
- Technical details: `RETURN_REFUND_NOTIFICATION_FIX.md`
- Tagalog guide: `AYOS_NA_RETURN_NOTIFICATION.md`

---

## Quick Test Command

```bash
# Start backend
cd backend
python app.py

# In another terminal, check logs:
tail -f backend_logs.txt

# Or watch console output for:
# - "Error sending seller notification"
# - "Error sending rejection notification"
# - "Error sending approval notification"
```

---

**Date:** May 21, 2026  
**Status:** READY FOR TESTING ✅  
**All Fixes Applied:** YES ✅
