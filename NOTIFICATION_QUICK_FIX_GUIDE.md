# 🔔 Notification System - Quick Fix Guide

## ✅ Ano ang Tapos Na (What's Done)

### Backend
- ✅ Complete notification database table with all columns
- ✅ All notification API endpoints working
- ✅ Complete notification functions for all scenarios
- ✅ SocketIO real-time support

### Mobile App
- ✅ Buyer notification screen (Shopee-style, beautiful)
- ✅ Rider notification screen (modern, smooth)
- ✅ API integration complete
- ✅ Mark as read, delete, filters working

## 🔧 Ano ang Kailangan Pa (What's Needed)

### 1. Test All Notifications ⏳

**Run the test script:**
```bash
cd backend
python test_all_notifications.py
```

This will create test notifications for all scenarios.

### 2. Verify Mobile App ⏳

**Buyer App:**
```bash
cd mobile_app
flutter run
# Login as buyer
# Go to notifications screen
# Check if notifications appear
```

**Rider App:**
```bash
# Login as rider
# Go to notifications screen  
# Check if notifications appear
```

### 3. Check Real-time Notifications ⏳

Make sure SocketIO is working:
- Place an order
- Check if notification appears immediately
- No need to refresh

## 🐛 Common Issues & Solutions

### Issue 1: Notifications Not Showing
**Solution:**
```sql
-- Check if notifications exist in database
SELECT * FROM notification ORDER BY created_at DESC LIMIT 10;

-- Check user_id matches
SELECT id, first_name, last_name, role FROM user WHERE id = YOUR_USER_ID;
```

### Issue 2: API Returns 500 Error
**Solution:**
```bash
# Check backend logs
cd backend
python app.py
# Look for errors in console
```

### Issue 3: Notifications Not Real-time
**Solution:**
- Check if SocketIO is running
- Check if mobile app is connected to SocketIO
- Verify backend URL in mobile app config

## 📝 Manual Testing Steps

### Test Order Flow
1. **Login as Buyer** → Place order
2. **Check Buyer Notifications** → Should see "Order Placed"
3. **Login as Seller** → Should see "New Order"
4. **Seller confirms order** → Buyer should see "Order Confirmed"
5. **Seller marks ready** → Buyer + All Riders should see notification
6. **Rider accepts** → Buyer + Seller should see notification
7. **Rider delivers** → Buyer + Seller should see notification
8. **Buyer confirms** → Seller + Rider should see notification with earnings

### Test Product Flow
1. **Seller adds product** → Admin should see notification
2. **Admin approves** → Seller should see "Product Approved"
3. **Product low stock** → Seller should see "Low Stock Alert"

### Test Payment Flow
1. **Buyer pays** → Seller should see "Payment Received"
2. **Order completed** → Rider should see "Earnings Credited"

## 🚀 Quick Commands

### Create Test Notifications (SQL)
```sql
-- Buyer notification
INSERT INTO notification (user_id, title, message, type, is_read, created_at)
VALUES (YOUR_BUYER_ID, 'Test Order', 'Your order #123 has been placed', 'order', false, NOW());

-- Seller notification
INSERT INTO notification (user_id, title, message, type, is_read, created_at)
VALUES (YOUR_SELLER_ID, 'New Order', 'You have a new order #123', 'order', false, NOW());

-- Rider notification
INSERT INTO notification (user_id, title, message, type, is_read, created_at)
VALUES (YOUR_RIDER_ID, 'New Delivery', 'Order #123 ready for pickup', 'order', false, NOW());
```

### Check Notification Counts
```sql
-- Total notifications
SELECT COUNT(*) FROM notification;

-- Unread notifications
SELECT COUNT(*) FROM notification WHERE is_read = false;

-- By user role
SELECT u.role, COUNT(n.id) as count
FROM notification n
JOIN user u ON n.user_id = u.id
GROUP BY u.role;

-- By type
SELECT type, COUNT(*) as count
FROM notification
GROUP BY type;
```

### Clear All Notifications (for testing)
```sql
-- Delete all notifications
DELETE FROM notification;

-- Or just mark all as read
UPDATE notification SET is_read = true;
```

## 📊 Notification Coverage Checklist

### Buyer Notifications
- [x] Order Placed
- [x] Order Confirmed
- [x] Order Processing
- [x] Ready for Pickup
- [x] Rider Assigned
- [x] Out for Delivery
- [x] Delivered
- [x] Payment Confirmed
- [x] Return Approved/Rejected
- [x] Refund Processed
- [x] Promotions
- [x] New Messages

### Seller Notifications
- [x] New Order
- [x] Payment Received
- [x] Order Picked Up
- [x] Order Delivered
- [x] Order Completed
- [x] Product Approved/Rejected
- [x] Low Stock Alert
- [x] Out of Stock
- [x] Return Requested
- [x] Order Cancelled
- [x] New Messages

### Rider Notifications
- [x] New Delivery Available
- [x] Delivery Completed
- [x] Earnings Credited
- [x] Delivery Cancelled
- [x] Bonus Earned
- [x] New Messages

### Admin Notifications (Website)
- [x] New Registration
- [x] New Seller Application
- [x] New Product Pending
- [x] Brand Added
- [x] Product Deleted

## 🎯 Next Actions

1. **Run Test Script** ✅
   ```bash
   cd backend
   python test_all_notifications.py
   ```

2. **Check Mobile App** ✅
   - Login as buyer → check notifications
   - Login as rider → check notifications

3. **Test Real Order Flow** ✅
   - Place actual order
   - Verify notifications at each step

4. **Check Website** ✅
   - Login as admin → check notifications
   - Login as seller → check notifications

## 📞 Support

If may problema:
1. Check backend logs (`python app.py`)
2. Check mobile app logs (Flutter console)
3. Check database (`SELECT * FROM notification`)
4. Check API response (Postman/curl)

## ✅ Success Criteria

Notification system is working if:
- ✅ Notifications appear in mobile app
- ✅ Notifications appear in real-time (no refresh needed)
- ✅ Mark as read works
- ✅ Delete works
- ✅ Filters work
- ✅ All user roles receive appropriate notifications
- ✅ Deep links navigate correctly

---

**Status**: 🟢 READY FOR TESTING  
**Date**: May 21, 2026  
**Next**: Run test script and verify mobile app
