# Return/Refund Notification Fix

## Problem Summary

### Issue 1: Seller Not Receiving Notification When Buyer Requests Return
**Current Behavior:** Buyer submits return/refund request, but seller doesn't receive notification  
**Expected Behavior:** Seller should receive notification immediately when return is requested

### Issue 2: Buyer Not Receiving Notification When Seller Rejects Return
**Current Behavior:** Seller rejects return request, but buyer doesn't receive notification  
**Expected Behavior:** Buyer should receive notification when return is rejected

## Root Causes

### Problem 1: Return Request Notification
**Location:** `app.py` line ~14060

**Current Code:**
```python
# Notify parties and emit realtime update
push_notification(item.product.seller_id, f'Return/Refund requested for Order #{order.id} — {item.product.name}.')
push_notification(order.buyer_id, f'Return/Refund request RR-{rr.id} submitted.')
_emit_return_update(rr)
```

**Issue:** Using `push_notification()` which may not be working correctly. Should use the proper notification system from `shopee_notification_system.py`

### Problem 2: Return Rejection Notification
**Location:** `app.py` line ~14254

**Current Code:**
```python
push_notification(rr.buyer_id, f'Return request RR-{rr.id} was rejected. Reason: {rr.seller_response_reason}')
```

**Issue:** Same as above - using `push_notification()` instead of proper notification system

## Solution

### Fix 1: Update Return Request Submission (Buyer → Seller)

**File:** `backend/app.py`  
**Location:** Around line 14060

**Replace:**
```python
# Notify parties and emit realtime update
push_notification(item.product.seller_id, f'Return/Refund requested for Order #{order.id} — {item.product.name}.')
push_notification(order.buyer_id, f'Return/Refund request RR-{rr.id} submitted.')
_emit_return_update(rr)
```

**With:**
```python
# Notify seller about return request
try:
    from shopee_notification_system import create_notification
    create_notification(
        user_id=item.product.seller_id,
        title="Return/Refund Request",
        message=f'Buyer requested return/refund for Order #{order.id} — {item.product.name}. Reason: {reason}',
        notification_type='order',
        order_id=order.id,
        action_url=f'/seller/returns/{rr.id}'
    )
except Exception as e:
    print(f"Error sending seller notification: {e}")
    # Fallback to push_notification
    push_notification(item.product.seller_id, f'Return/Refund requested for Order #{order.id} — {item.product.name}.')

# Notify buyer about submission
try:
    from shopee_notification_system import create_notification
    create_notification(
        user_id=order.buyer_id,
        title="Return Request Submitted",
        message=f'Your return/refund request RR-{rr.id} has been submitted. Seller will review it soon.',
        notification_type='order',
        order_id=order.id,
        action_url=f'/buyer/returns/{rr.id}'
    )
except Exception as e:
    print(f"Error sending buyer notification: {e}")
    push_notification(order.buyer_id, f'Return/Refund request RR-{rr.id} submitted.')

_emit_return_update(rr)
```

### Fix 2: Update Return Rejection (Seller → Buyer)

**File:** `backend/app.py`  
**Location:** Around line 14254

**Replace:**
```python
push_notification(rr.buyer_id, f'Return request RR-{rr.id} was rejected. Reason: {rr.seller_response_reason}')
```

**With:**
```python
# Notify buyer about rejection
try:
    from shopee_notification_system import create_notification
    create_notification(
        user_id=rr.buyer_id,
        title="Return Request Rejected",
        message=f'Your return request RR-{rr.id} for Order #{rr.order_id} was rejected. Reason: {rr.seller_response_reason}',
        notification_type='order',
        order_id=rr.order_id,
        action_url=f'/buyer/orders/{rr.order_id}'
    )
except Exception as e:
    print(f"Error sending rejection notification: {e}")
    # Fallback to push_notification
    push_notification(rr.buyer_id, f'Return request RR-{rr.id} was rejected. Reason: {rr.seller_response_reason}')
```

### Fix 3: Update Return Approval (Seller → Buyer)

**File:** `backend/app.py`  
**Location:** Find `seller_return_approve` function

**Add notification:**
```python
# Notify buyer about approval
try:
    from shopee_notification_system import create_notification
    create_notification(
        user_id=rr.buyer_id,
        title="Return Request Approved",
        message=f'Your return request RR-{rr.id} for Order #{rr.order_id} has been approved. Please prepare the item for pickup.',
        notification_type='order',
        order_id=rr.order_id,
        action_url=f'/buyer/returns/{rr.id}'
    )
except Exception as e:
    print(f"Error sending approval notification: {e}")
```

## Additional Improvements

### Add Notification for Return Pickup Scheduled
When rider is assigned to pick up return:

```python
# Notify buyer
create_notification(
    user_id=rr.buyer_id,
    title="Return Pickup Scheduled",
    message=f'A rider has been assigned to pick up your return RR-{rr.id}.',
    notification_type='order',
    order_id=rr.order_id,
    action_url=f'/buyer/returns/{rr.id}'
)

# Notify seller
create_notification(
    user_id=rr.seller_id,
    title="Return Pickup in Progress",
    message=f'Rider is picking up return RR-{rr.id} from buyer.',
    notification_type='order',
    order_id=rr.order_id,
    action_url=f'/seller/returns/{rr.id}'
)
```

### Add Notification for Return Received by Seller
When seller marks return as received:

```python
create_notification(
    user_id=rr.buyer_id,
    title="Return Received by Seller",
    message=f'Seller has received your return RR-{rr.id}. Refund will be processed soon.',
    notification_type='order',
    order_id=rr.order_id,
    action_url=f'/buyer/returns/{rr.id}'
)
```

### Add Notification for Refund Processed
When refund is completed:

```python
create_notification(
    user_id=rr.buyer_id,
    title="Refund Processed",
    message=f'Refund of ₱{refund_amount:.2f} for return RR-{rr.id} has been credited to your wallet.',
    notification_type='payment',
    order_id=rr.order_id,
    action_url=f'/buyer/wallet'
)
```

## Testing Checklist

### Test 1: Buyer Requests Return
1. [ ] Login as buyer
2. [ ] Go to completed order
3. [ ] Click "Request Return/Refund"
4. [ ] Fill form and submit
5. [ ] **Expected:** Buyer sees success message
6. [ ] **Expected:** Seller receives notification immediately
7. [ ] Check seller's notification bell icon
8. [ ] Check seller's notifications page

### Test 2: Seller Rejects Return
1. [ ] Login as seller
2. [ ] Go to Returns section
3. [ ] Open pending return request
4. [ ] Click "Reject" and provide reason
5. [ ] **Expected:** Seller sees success message
6. [ ] **Expected:** Buyer receives notification immediately
7. [ ] Check buyer's notification bell icon
8. [ ] Check buyer's notifications page

### Test 3: Seller Approves Return
1. [ ] Login as seller
2. [ ] Go to Returns section
3. [ ] Open pending return request
4. [ ] Click "Approve"
5. [ ] **Expected:** Seller sees success message
6. [ ] **Expected:** Buyer receives notification immediately
7. [ ] Check buyer's notification bell icon

### Test 4: Real-time Updates
1. [ ] Open buyer account in one browser
2. [ ] Open seller account in another browser
3. [ ] Buyer submits return request
4. [ ] **Expected:** Seller's notification badge updates in real-time (via Socket.IO)
5. [ ] Seller rejects return
6. [ ] **Expected:** Buyer's notification badge updates in real-time

## Database Verification

### Check Notifications Table
```sql
-- Check if notifications are being created
SELECT * FROM notification 
WHERE message LIKE '%return%' OR message LIKE '%refund%'
ORDER BY created_at DESC 
LIMIT 10;

-- Check unread notifications for seller
SELECT * FROM notification 
WHERE user_id = [SELLER_ID] 
AND is_read = FALSE 
AND (message LIKE '%return%' OR message LIKE '%refund%')
ORDER BY created_at DESC;

-- Check unread notifications for buyer
SELECT * FROM notification 
WHERE user_id = [BUYER_ID] 
AND is_read = FALSE 
AND (message LIKE '%reject%' OR message LIKE '%approv%')
ORDER BY created_at DESC;
```

### Check Return Requests
```sql
-- Check return request status
SELECT 
    rr.id,
    rr.order_id,
    rr.buyer_id,
    rr.seller_id,
    rr.status,
    rr.reason,
    rr.seller_response_reason,
    rr.created_at,
    rr.processed_at
FROM return_request rr
ORDER BY rr.created_at DESC
LIMIT 10;
```

## Expected Behavior After Fix

### When Buyer Requests Return:
✅ Buyer sees success message  
✅ Seller receives notification immediately  
✅ Seller's notification bell shows unread count  
✅ Notification appears in seller's notification list  
✅ Notification has link to return detail page  
✅ Real-time Socket.IO update (if seller is online)

### When Seller Rejects Return:
✅ Seller sees success message  
✅ Buyer receives notification immediately  
✅ Buyer's notification bell shows unread count  
✅ Notification appears in buyer's notification list  
✅ Notification shows rejection reason  
✅ Notification has link to order detail page  
✅ Real-time Socket.IO update (if buyer is online)

### When Seller Approves Return:
✅ Seller sees success message  
✅ Buyer receives notification immediately  
✅ Buyer's notification bell shows unread count  
✅ Notification appears in buyer's notification list  
✅ Notification has link to return detail page  
✅ Real-time Socket.IO update (if buyer is online)

## Files to Modify

1. **`backend/app.py`**
   - Line ~14060: Return request submission
   - Line ~14254: Return rejection
   - Find and update: Return approval function

## Troubleshooting

### If notifications still not appearing:

1. **Check if `create_notification` is imported:**
   ```python
   from shopee_notification_system import create_notification
   ```

2. **Check backend console for errors:**
   ```
   Error sending seller notification: ...
   Error sending rejection notification: ...
   ```

3. **Check if Socket.IO is running:**
   ```python
   # In app.py, verify socketio is initialized
   socketio = SocketIO(app, cors_allowed_origins="*")
   ```

4. **Check notification table exists:**
   ```sql
   SHOW TABLES LIKE 'notification';
   DESC notification;
   ```

5. **Test notification system directly:**
   ```python
   # In Python shell or test route
   from shopee_notification_system import create_notification
   create_notification(
       user_id=1,
       title="Test",
       message="Test notification",
       notification_type='system'
   )
   ```

## Alternative: Use Existing Notification Functions

If the above doesn't work, you can also use the existing notification functions from `shopee_notification_system.py`:

```python
# For return requested
from shopee_notification_system import notify_return_requested
notify_return_requested(order, reason=reason)

# For return rejected
from shopee_notification_system import notify_return_rejected
notify_return_rejected(order, reason=rr.seller_response_reason)

# For return approved
from shopee_notification_system import notify_return_approved
notify_return_approved(order)
```

**Note:** These functions expect an `order` object, not a `ReturnRequest` object. You may need to pass `rr.order` instead.

---

**Status:** Ready to implement  
**Priority:** HIGH - Critical user experience issue  
**Estimated Time:** 15-30 minutes
