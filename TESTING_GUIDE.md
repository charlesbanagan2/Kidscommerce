# 🧪 QUICK TESTING GUIDE - Rider Order Flow

## Prerequisites
- Backend server running on port 5000
- Mobile app installed on device/emulator
- Test accounts: buyer, seller, rider

---

## Test Scenario: Complete Order Flow

### Step 1: Create Order (Buyer)
1. Login as **buyer**
2. Add product to cart
3. Checkout with COD
4. **Expected:** Order created with status `pending`

### Step 2: Mark Ready for Pickup (Seller)
1. Login as **seller**
2. Go to Orders → Find the order
3. Click "Mark as Ready for Pickup"
4. **Expected:** Order status → `ready_for_pickup`

### Step 3: Accept Order (Rider) ⭐ FIXED
1. Login as **rider** in mobile app
2. Go to "Available Orders" tab
3. Tap on the order
4. Tap "Accept Order"
5. **Expected:**
   - ✅ No 500 error
   - ✅ Order moves to "Active Deliveries"
   - ✅ Order status = `in_transit`
   - ✅ Buyer receives notification
   - ✅ Seller receives notification

### Step 4: Mark as Delivered (Rider) ⭐ NEW
1. Stay logged in as **rider**
2. Go to "Active Deliveries" tab
3. Tap "Mark as Delivered"
4. **Expected:**
   - ✅ Order status = `delivered`
   - ✅ Buyer receives notification
   - ✅ Seller receives notification

### Step 5: Confirm Receipt (Buyer) ⭐ ENHANCED
1. Login as **buyer** in mobile app
2. Go to "To Receive" tab
3. Tap "Order Received"
4. **Expected:**
   - ✅ Order status = `completed`
   - ✅ Order moves to "Completed" tab
   - ✅ Rider receives notification
   - ✅ Seller receives notification
   - ✅ **Commissions released:**
     - Rider: 15%
     - Seller: 80%
     - Admin: 5%

### Step 6: Verify Commissions (Rider)
1. Stay logged in as **rider**
2. Go to "Earnings" or "Wallet"
3. **Expected:**
   - ✅ Commission appears (15% of order total)
   - ✅ Can see transaction history

---

## Quick Debug Commands

### Check Backend Logs
```bash
# Windows
cd c:\Users\mnban\Documents\kids\backend
python app.py
# Watch for errors in console
```

### Check Order Status in Database
```python
# In Python shell
from app import db, Order
order = Order.query.get(ORDER_ID)
print(f"Status: {order.status}")
print(f"Rider ID: {order.rider_id}")
print(f"Rider Earnings: {order.rider_earnings}")
```

### Check Wallet Transactions
```python
from app import db, WalletTransaction
txns = WalletTransaction.query.filter_by(order_id=ORDER_ID).all()
for t in txns:
    print(f"User {t.user_id}: {t.amount} ({t.source})")
```

---

## Common Issues & Solutions

### Issue: 500 Error on Accept Order
**Solution:** ✅ FIXED - Typo in `update_data_` corrected

### Issue: Order Not Appearing in Buyer's Tab
**Solution:** Check order status - should be `in_transit` after acceptance

### Issue: Commission Not Released
**Solution:** Buyer must confirm receipt (status → `completed`)

### Issue: Notifications Not Received
**Solution:** Check `push_notification()` function and SocketIO connection

---

## API Testing with cURL

### Accept Order
```bash
curl -X POST http://localhost:5000/api/v1/rider/orders/123/accept \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Mark as Delivered
```bash
curl -X POST http://localhost:5000/api/v1/rider/orders/123/mark-delivered \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Confirm Delivery (Buyer)
```bash
curl -X POST http://localhost:5000/api/v1/buyer/orders/123/confirm-delivery \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Expected Response Examples

### Success Response
```json
{
  "success": true,
  "message": "Order accepted successfully",
  "order": {
    "id": 123,
    "status": "in_transit",
    "rider_id": 5
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Order not found"
}
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] Order status = `completed`
- [ ] Rider commission in wallet (15%)
- [ ] Seller commission in wallet (80%)
- [ ] Admin commission in wallet (5%)
- [ ] All notifications sent
- [ ] Order in correct tabs for all users
- [ ] No errors in backend logs
- [ ] Mobile app shows correct status

---

## Test Data Example

**Order Total:** ₱1,000

**Expected Commissions:**
- Rider: ₱150 (15%)
- Seller: ₱800 (80%)
- Admin: ₱50 (5%)

**Status Flow:**
```
pending → ready_for_pickup → in_transit → delivered → completed
```

---

## Need Help?

1. Check backend logs for errors
2. Verify API endpoints are correct
3. Check database for order status
4. Verify tokens are valid
5. Review RIDER_ORDER_FLOW_COMPLETE.md for details

---

**Status:** ✅ All fixes implemented and ready for testing
