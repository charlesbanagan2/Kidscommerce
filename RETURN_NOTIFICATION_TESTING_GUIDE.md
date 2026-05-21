# Return Notification Testing Guide

## Quick Test in Mobile App

### Test Scenario 1: Return Rejection
1. **As Buyer**:
   - Create a return request for a delivered order
   - Note the order number

2. **As Seller**:
   - Go to Returns section
   - Find the return request
   - Click "Reject" and provide a reason
   - Submit rejection

3. **As Buyer**:
   - Check notifications (bell icon)
   - Should see: "Your return request for Order #X was rejected. Reason: [reason]"
   - Notification type: `return_rejected`

### Test Scenario 2: Return Approval
1. **As Buyer**:
   - Create a return request for a delivered order
   - Note the order number

2. **As Seller**:
   - Go to Returns section
   - Find the return request
   - Click "Approve"
   - Confirm approval

3. **As Buyer**:
   - Check notifications (bell icon)
   - Should see: "Your return request for Order #X has been approved. The item is now refunded."
   - Notification type: `return_approved`

## Backend Verification Commands

### Check All Notifications
```bash
cd backend
python simple_notification_check.py
```

### Check Specific Return Request
```bash
cd backend
python -c "from app import app, db, ReturnRequest, Notification; app.app_context().push(); rr = ReturnRequest.query.get(RETURN_ID); notifs = Notification.query.filter_by(user_id=rr.buyer_id, order_id=rr.order_id).all(); [print(f'{n.type}: {n.message}') for n in notifs]"
```
Replace `RETURN_ID` with actual return request ID.

### Fix Sequence if Needed
```bash
cd backend
python -c "from app import app, db, force_fix_sequence_for_table; app.app_context().push(); force_fix_sequence_for_table('notification')"
```

## Expected Notification Format

### Rejection Notification
```json
{
  "type": "return_rejected",
  "title": "Return Request Rejected",
  "message": "Your return request for Order #54 was rejected. Reason: Product already used",
  "link": "/buyer/orders/54",
  "order_id": 54,
  "user_id": 25
}
```

### Approval Notification
```json
{
  "type": "return_approved",
  "title": "Return Approved & Refunded",
  "message": "Your return request for Order #55 has been approved. The item is now refunded.",
  "link": "/buyer/orders/55",
  "order_id": 55,
  "user_id": 60
}
```

## Troubleshooting

### Issue: No notification received
**Check 1**: Verify notification was created in database
```bash
cd backend
python -c "from app import app, db, Notification; app.app_context().push(); n = Notification.query.order_by(Notification.id.desc()).first(); print(f'Latest: {n.type} - {n.message}')"
```

**Check 2**: Verify user ID matches
```bash
cd backend
python -c "from app import app, db, ReturnRequest; app.app_context().push(); rr = ReturnRequest.query.get(RETURN_ID); print(f'Buyer ID: {rr.buyer_id}')"
```

**Check 3**: Check for sequence errors in logs
Look for: `duplicate key value violates unique constraint`
Fix: Run sequence fix command above

### Issue: Notification created but not showing in app
**Check 1**: Verify notification is for correct user
```bash
cd backend
python -c "from app import app, db, Notification; app.app_context().push(); n = Notification.query.filter_by(type='return_rejected').order_by(Notification.id.desc()).first(); print(f'User ID: {n.user_id}, Message: {n.message}')"
```

**Check 2**: Check if notification is marked as read
```bash
cd backend
python -c "from app import app, db, Notification; app.app_context().push(); n = Notification.query.order_by(Notification.id.desc()).first(); print(f'Read: {n.is_read}')"
```

**Check 3**: Verify mobile app is polling notifications
- Check network tab in mobile app debugger
- Should see requests to `/api/notifications`

## API Endpoints

### Get Notifications (Mobile)
```
GET /api/notifications
Headers:
  Authorization: Bearer {token}
```

### Mark as Read
```
POST /api/notifications/{id}/read
Headers:
  Authorization: Bearer {token}
```

## Success Criteria

✅ Buyer receives notification within 1 second of seller action  
✅ Notification appears in mobile app notification list  
✅ Notification includes correct order number  
✅ Rejection notification includes seller's reason  
✅ Notification link navigates to correct order  
✅ Notification count badge updates  

## Common Test Data

### Test Users
- **Buyer**: Juan Buyer (ID: 25)
- **Seller**: KIDDOPIA PH (ID: 16)
- **Rider**: Juan Rider (ID: 28)

### Test Return Requests
- **Return #4**: Order #54, Status: rejected
- **Return #3**: Order #55, Status: refunded

## Monitoring in Production

### Daily Check
```bash
cd backend
python -c "from app import app, db, Notification; app.app_context().push(); from datetime import datetime, timedelta; today = datetime.utcnow().date(); count = Notification.query.filter(Notification.created_at >= today).count(); print(f'Notifications today: {count}')"
```

### Check Return Notifications
```bash
cd backend
python -c "from app import app, db, Notification; app.app_context().push(); count = Notification.query.filter(Notification.type.in_(['return_approved', 'return_rejected'])).count(); print(f'Total return notifications: {count}')"
```

---

**Last Updated**: May 21, 2026  
**Status**: Production Ready ✅
