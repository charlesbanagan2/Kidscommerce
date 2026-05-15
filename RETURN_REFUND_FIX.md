# 🔄 Return & Refund System Fix

## 🐛 Problem Identified

### Issue 1: Approved Returns
- When seller **approves** return request
- Item should appear in "Returns & Refunds" section
- Status should show as "Refunded" or "Return Approved"
- Currently: Shows as "Completed"

### Issue 2: Rejected Returns  
- When seller **rejects** return request
- Item should remain in "Completed" orders
- Status should show as "Completed" (not refunded)
- Currently: Also shows as "Completed"

---

## 🔧 Solution

### Backend Changes Needed:

1. **Add "Returns" tab to Orders Screen**
2. **Update order status when return is approved/rejected**
3. **Filter orders properly in mobile app**

### Status Flow:

```
Order Completed
    ↓
Buyer Requests Return
    ↓
    ├─→ Seller Approves
    │   ├─→ Order status: "return_approved"
    │   ├─→ Shows in: Returns & Refunds tab
    │   └─→ Display: "Refunded" or "Return Approved"
    │
    └─→ Seller Rejects
        ├─→ Order status: "completed" (unchanged)
        ├─→ Shows in: Completed tab
        └─→ Display: "Completed"
```

---

## 📱 Implementation

### Step 1: Add Returns Tab to Orders Screen
### Step 2: Update Backend Return Approval Logic
### Step 3: Update Mobile App Filtering

---

## Files to Modify:

1. `backend/app.py` - Return approval/rejection routes
2. `mobile_app/lib/screens/buyer_app/orders_screen.dart` - Add returns tab
3. `mobile_app/lib/providers/buyer_provider.dart` - Fetch returns with orders

---

**Status:** Ready to implement
