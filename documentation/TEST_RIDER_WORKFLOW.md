# Rider Workflow Test Guide

## Complete End-to-End Test: Buyer Purchase → Seller Ready → Riders See → One Accepts

---

## Test Environment Setup

### Prerequisites
- ✅ Backend running on `http://192.168.1.20:5000`
- ✅ PostgreSQL database (required for row-level locking)
- ✅ Socket.IO enabled
- ✅ At least 2 rider accounts (approved status)
- ✅ At least 1 seller account with products
- ✅ At least 1 buyer account

### Test Accounts Needed
```
Buyer: buyer@test.com / buyer123
Seller: seller@test.com / seller123
Rider 1: rider1@test.com / rider123
Rider 2: rider2@test.com / rider123
```

---

## Test Workflow

### Step 1: Buyer Makes Purchase

**Action**: Buyer places an order

**Expected Result**:
- ✅ Order created with status: `pending`
- ✅ Order appears in seller's dashboard
- ✅ Order does NOT appear in rider's available orders yet

**How to Test**:
1. Login as buyer in mobile app
2. Add products to cart
3. Proceed to checkout
4. Complete payment (COD)
5. Verify order confirmation

**Database Check**:
```sql
SELECT id, status, buyer_id, seller_id, rider_id, total_amount 
FROM "order" 
WHERE buyer_id = <buyer_id> 
ORDER BY created_at DESC 
LIMIT 1;
```

**Expected**:
- status = 'pending'
- rider_id = NULL

---

### Step 2: Seller Accepts Order

**Action**: Seller marks order as processing

**Expected Result**:
- ✅ Order status changes to `processing`
- ✅ Order still does NOT appear in rider's available orders

**How to Test**:
1. Login as seller in web dashboard
2. Go to Orders section
3. Find the new order
4. Click "Accept Order" or "Mark as Processing"

**Database Check**:
```sql
SELECT id, status, rider_id 
FROM "order" 
WHERE id = <order_id>;
```

**Expected**:
- status = 'processing'
- rider_id = NULL

---

### Step 3: Seller Marks Ready for Pickup ⭐ CRITICAL

**Action**: Seller marks order as ready for pickup

**Expected Result**:
- ✅ Order status changes to `ready_for_pickup`
- ✅ Socket.IO event `new_order_available` emitted to ALL riders
- ✅ Order appears in ALL riders' "Available Orders" list
- ✅ Real-time notification shown to all riders

**How to Test**:
1. Keep 2+ rider mobile apps open and logged in
2. Both riders should be on "Available Orders" screen
3. Seller clicks "Mark Ready for Pickup" button
4. **Watch both rider apps simultaneously**

**Expected on Rider Apps**:
- 🔔 Green notification: "New order available!"
- 📦 Order card appears at top of list
- 💰 Shows delivery fee (15% of order total)
- 📍 Shows pickup address (seller)
- 📍 Shows delivery address (buyer)

**Database Check**:
```sql
SELECT id, status, rider_id, seller_id, buyer_id, total_amount
FROM "order" 
WHERE id = <order_id>;
```

**Expected**:
- status = 'ready_for_pickup'
- rider_id = NULL

**Socket.IO Event Check** (Backend Logs):
```
[Socket.IO] Emitting new_order_available to riders room
Order ID: <order_id>
Buyer: <buyer_name>
Seller: <seller_name>
Amount: ₱<amount>
```

---

### Step 4: Multiple Riders Try to Accept (FCFS Test) ⭐ CRITICAL

**Action**: 2+ riders click "Accept Order" button simultaneously

**Expected Result**:
- ✅ **ONLY ONE** rider successfully accepts
- ✅ Other riders get error: "Order already taken by another rider"
- ✅ Order disappears from all other riders' lists
- ✅ Socket.IO event `order_claimed` emitted
- ✅ Winning rider sees order in "My Deliveries"

**How to Test**:
1. Have 2 riders ready with finger on "Accept Order" button
2. Click both buttons at the SAME TIME (within 1 second)
3. Watch the results

**Expected Results**:

**Rider 1 (Winner)**:
- ✅ Success message: "Order accepted! Check 'My Deliveries' tab"
- ✅ Order disappears from Available Orders
- ✅ Order appears in My Deliveries with status "In Transit"

**Rider 2 (Loser)**:
- ⚠️ Orange notification: "Order already taken by another rider"
- ✅ Order disappears from Available Orders
- ✅ Order does NOT appear in My Deliveries

**Database Check**:
```sql
SELECT id, status, rider_id 
FROM "order" 
WHERE id = <order_id>;
```

**Expected**:
- status = 'in_transit'
- rider_id = <winning_rider_id> (NOT NULL)

**Backend Logs Check**:
```
[FCFS] Rider <rider1_id> attempting to accept order <order_id>
[FCFS] Row-level lock acquired
[FCFS] Order accepted by rider <rider1_id>
[Socket.IO] Broadcasting order_claimed event

[FCFS] Rider <rider2_id> attempting to accept order <order_id>
[FCFS] Order already claimed by another rider
[FCFS] Returning 409 Conflict
```

---

### Step 5: Rider Completes Delivery

**Action**: Winning rider marks delivery as complete

**Expected Result**:
- ✅ Order status changes to `delivered`
- ✅ Rider earnings calculated (15% of total)
- ✅ Order moves to completed deliveries
- ✅ Buyer can confirm receipt

**How to Test**:
1. Winning rider opens "My Deliveries"
2. Finds the order
3. Clicks "Delivered" button
4. Confirms action

**Database Check**:
```sql
SELECT id, status, rider_id, rider_earnings 
FROM "order" 
WHERE id = <order_id>;
```

**Expected**:
- status = 'delivered'
- rider_id = <winning_rider_id>
- rider_earnings = total_amount * 0.15

---

## Quick Test Checklist

### ✅ Pre-Test Setup
- [ ] Backend running with PostgreSQL
- [ ] Socket.IO enabled and working
- [ ] 2+ rider accounts approved
- [ ] 1 seller account with products
- [ ] 1 buyer account

### ✅ Test Execution
- [ ] Buyer places order → status: pending
- [ ] Seller accepts order → status: processing
- [ ] Seller marks ready → status: ready_for_pickup
- [ ] **ALL riders see order in Available Orders**
- [ ] **Real-time notification appears on all rider apps**
- [ ] 2 riders click Accept simultaneously
- [ ] **Only 1 rider succeeds**
- [ ] **Other rider gets "already taken" error**
- [ ] Order disappears from all riders' Available Orders
- [ ] Winning rider sees order in My Deliveries
- [ ] Winning rider completes delivery → status: delivered

---

## Common Issues & Solutions

### Issue 1: Order Not Appearing in Rider's Available Orders

**Possible Causes**:
- Order status is not `ready_for_pickup`
- Rider is not approved (status != 'approved')
- Socket.IO not connected
- API endpoint not returning order

**Debug Steps**:
```sql
-- Check order status
SELECT id, status FROM "order" WHERE id = <order_id>;

-- Check rider approval status
SELECT id, email, status FROM "user" WHERE role = 'rider';

-- Check if order meets criteria
SELECT id, status, rider_id 
FROM "order" 
WHERE status = 'ready_for_pickup' AND rider_id IS NULL;
```

**Solution**:
- Ensure order status is exactly `ready_for_pickup`
- Ensure rider status is `approved`
- Check backend logs for Socket.IO connection
- Restart rider app to reconnect Socket.IO

---

### Issue 2: Both Riders Accept Order (FCFS Failed)

**Possible Causes**:
- Using SQLite instead of PostgreSQL
- Row-level locking not working
- Transaction isolation level incorrect

**Debug Steps**:
```python
# Check database type
from app import db
print(db.engine.url)  # Should show postgresql://
```

**Solution**:
- **MUST use PostgreSQL** (SQLite doesn't support row-level locking)
- Verify `with_for_update()` is in accept order code
- Check transaction isolation level

---

### Issue 3: Socket.IO Not Working

**Symptoms**:
- No real-time notifications
- Order doesn't appear until manual refresh

**Debug Steps**:
```python
# Backend: Check Socket.IO initialization
from app import socketio
print(socketio)  # Should show SocketIO instance

# Check if riders joined room
# Backend logs should show:
# [Socket.IO] Rider <id> joined riders room
```

**Solution**:
- Ensure `socketio.run(app)` instead of `app.run()`
- Check CORS settings for Socket.IO
- Verify rider app calls `RiderService.initializeSocket()`
- Check network connectivity

---

### Issue 4: Order Appears But Can't Accept

**Possible Causes**:
- Rider not authenticated
- Token expired
- Rider not approved

**Debug Steps**:
```dart
// Mobile app: Check authentication
final authProvider = Provider.of<AuthProvider>(context, listen: false);
print('Authenticated: ${authProvider.isAuthenticated}');
print('Token: ${authProvider.tokens?['access_token']}');
print('User Role: ${authProvider.user?.role}');
```

**Solution**:
- Re-login to get fresh token
- Verify rider status is 'approved' in database
- Check backend logs for authorization errors

---

## API Endpoint Tests

### Test 1: Get Available Orders
```bash
curl -X GET http://192.168.1.20:5000/api/rider/available-orders \
  -H "Authorization: Bearer <rider_token>"
```

**Expected Response**:
```json
{
  "success": true,
  "orders": [
    {
      "id": 123,
      "buyer_name": "John Doe",
      "buyer_phone": "+639123456789",
      "delivery_address": "123 Main St",
      "total_amount": 1000.0,
      "items": [...],
      "seller_info": {...}
    }
  ]
}
```

---

### Test 2: Accept Order (FCFS)
```bash
curl -X POST http://192.168.1.20:5000/api/rider/accept-order/123 \
  -H "Authorization: Bearer <rider_token>"
```

**Expected Response (Success)**:
```json
{
  "success": true,
  "message": "Order accepted successfully",
  "order": {
    "id": 123,
    "status": "in_transit",
    "rider_id": 456
  }
}
```

**Expected Response (Already Taken)**:
```json
{
  "success": false,
  "conflict": true,
  "error": "This order has already been accepted by another rider"
}
```

---

### Test 3: Get My Deliveries
```bash
curl -X GET http://192.168.1.20:5000/api/rider/my-deliveries \
  -H "Authorization: Bearer <rider_token>"
```

**Expected Response**:
```json
{
  "success": true,
  "deliveries": [
    {
      "id": 123,
      "status": "in_transit",
      "buyer_name": "John Doe",
      "delivery_address": "123 Main St",
      "total_amount": 1000.0,
      "rider_earnings": 150.0
    }
  ]
}
```

---

## Database Verification Queries

### Check Order Flow
```sql
-- View complete order history
SELECT 
  id,
  status,
  buyer_id,
  seller_id,
  rider_id,
  total_amount,
  rider_earnings,
  created_at,
  updated_at
FROM "order"
WHERE id = <order_id>;
```

### Check Rider Earnings
```sql
-- View rider's total earnings
SELECT 
  u.id,
  u.email,
  COUNT(o.id) as total_deliveries,
  SUM(o.rider_earnings) as total_earnings
FROM "user" u
LEFT JOIN "order" o ON o.rider_id = u.id AND o.status = 'delivered'
WHERE u.role = 'rider'
GROUP BY u.id, u.email;
```

### Check Available Orders
```sql
-- Orders available for pickup
SELECT 
  id,
  status,
  buyer_id,
  seller_id,
  rider_id,
  total_amount
FROM "order"
WHERE status = 'ready_for_pickup' 
  AND rider_id IS NULL
ORDER BY created_at ASC;
```

---

## Success Criteria

### ✅ All Tests Must Pass

1. **Order Visibility**
   - [ ] Order appears in ALL riders' apps when marked ready
   - [ ] Real-time notification shown to all riders
   - [ ] Order details are complete and accurate

2. **FCFS Logic**
   - [ ] Only ONE rider can accept the order
   - [ ] Other riders get "already taken" error
   - [ ] Order disappears from all riders immediately
   - [ ] No duplicate assignments in database

3. **Real-Time Updates**
   - [ ] Socket.IO notifications work instantly
   - [ ] No manual refresh needed
   - [ ] Order list updates automatically

4. **Status Flow**
   - [ ] pending → processing → ready_for_pickup → in_transit → delivered
   - [ ] Each status change is logged correctly
   - [ ] Rider earnings calculated correctly

5. **Error Handling**
   - [ ] Graceful handling of race conditions
   - [ ] Clear error messages to users
   - [ ] No crashes or freezes

---

## Performance Test

### Stress Test: 5 Riders, 1 Order

**Setup**:
- 5 rider accounts logged in
- All on Available Orders screen
- 1 order marked ready for pickup

**Test**:
- All 5 riders click Accept simultaneously

**Expected**:
- ✅ Exactly 1 rider succeeds
- ✅ 4 riders get "already taken" error
- ✅ No database corruption
- ✅ No duplicate assignments

**Database Verification**:
```sql
-- Should return exactly 1 row
SELECT rider_id, COUNT(*) 
FROM "order" 
WHERE id = <order_id>
GROUP BY rider_id;
```

---

## Test Report Template

```
===========================================
RIDER WORKFLOW TEST REPORT
===========================================

Date: _______________
Tester: _______________
Backend Version: _______________
Mobile App Version: _______________

-------------------------------------------
TEST RESULTS
-------------------------------------------

1. Order Visibility: [ PASS / FAIL ]
   - All riders see order: [ YES / NO ]
   - Real-time notification: [ YES / NO ]
   - Notes: _______________________________

2. FCFS Logic: [ PASS / FAIL ]
   - Only 1 rider accepted: [ YES / NO ]
   - Others got error: [ YES / NO ]
   - Notes: _______________________________

3. Real-Time Updates: [ PASS / FAIL ]
   - Socket.IO working: [ YES / NO ]
   - Auto-refresh working: [ YES / NO ]
   - Notes: _______________________________

4. Status Flow: [ PASS / FAIL ]
   - All statuses correct: [ YES / NO ]
   - Earnings calculated: [ YES / NO ]
   - Notes: _______________________________

5. Error Handling: [ PASS / FAIL ]
   - Graceful errors: [ YES / NO ]
   - No crashes: [ YES / NO ]
   - Notes: _______________________________

-------------------------------------------
ISSUES FOUND
-------------------------------------------

1. _______________________________________
2. _______________________________________
3. _______________________________________

-------------------------------------------
OVERALL RESULT: [ PASS / FAIL ]
-------------------------------------------
```

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Deploy to production
2. Monitor real-world usage
3. Collect rider feedback
4. Optimize performance

### If Tests Fail ❌
1. Review backend logs
2. Check database queries
3. Verify Socket.IO connection
4. Test with different network conditions
5. Re-run tests after fixes

---

**READY TO TEST! 🚀**

Start with Step 1 and follow the workflow exactly as documented.
