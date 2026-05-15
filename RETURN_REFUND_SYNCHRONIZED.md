# ✅ SYNCHRONIZED RETURN & REFUND SCREENS

## 📋 OVERVIEW

Ang buyer at seller return screens ay **TUGMA NA** at **MAGKAPAREHAS** para walang error at confusion.

---

## 🎯 SYNCHRONIZED FEATURES

### 1. **Status Labels** (Parehas sa Buyer at Seller)
```
Status in DB    →  Display Label
─────────────────────────────────
submitted       →  PENDING
pending         →  PENDING
approved        →  APPROVED
rejected        →  REJECTED
```

### 2. **Status Colors** (Parehas sa Buyer at Seller)
```
PENDING   →  Orange (#FF9800)
APPROVED  →  Green  (#4CAF50)
REJECTED  →  Red    (#F44336)
```

### 3. **Status Messages** (Tugma ang Buyer at Seller)

#### PENDING Status:
**Buyer sees:**
```
⏰ Waiting for seller to review your request.
```

**Seller sees:**
```
[Approve] [Reject] buttons
```

#### APPROVED Status:
**Buyer sees:**
```
✅ Your return request was approved. The item is now refunded.
```

**Seller sees:**
```
✅ Return approved. Item is now refunded and moved to Returns tab.
```

#### REJECTED Status:
**Buyer sees:**
```
❌ Your return request was rejected by the seller.
```

**Seller sees:**
```
❌ Rejection Reason: [seller's reason here]
```

---

## 📱 BUYER SIDE SCREENS

### 1. **Returns List Screen** (`returns_index.dart`)

**Features:**
- ✅ Shows all return requests
- ✅ Color-coded status badges
- ✅ Status messages (pending/approved/rejected)
- ✅ Tap to view details
- ✅ Pull to refresh

**Card Layout:**
```
┌─────────────────────────────────────┐
│ Return #123              [PENDING]  │
│ Order #456                          │
├─────────────────────────────────────┤
│ Reason: Item damaged                │
│ Requested: 2025-01-15               │
│ Evidence: 3 file(s) attached        │
├─────────────────────────────────────┤
│ ⏰ Waiting for seller to review     │
└─────────────────────────────────────┘
```

**Status-Specific Messages:**
- **PENDING:** Orange box with clock icon
- **APPROVED:** Green box with checkmark icon
- **REJECTED:** Red box with X icon

---

### 2. **Return Request Screen** (`return_refund_screen.dart`)

**3-Step Wizard:**
1. **Select Items** - Choose products to return
2. **Reason & Evidence** - Upload photos/videos
3. **Review & Submit** - Confirm details

**After Submission:**
```
✅ Request Submitted!

Your return & refund request has been 
submitted successfully.

┌─────────────────────────────────┐
│ Request ID: RET-8901234         │
│ Status: Under Review            │
│ Expected Resolution: 2025-01-17 │
└─────────────────────────────────┘

[Back to Order]
```

---

## 🏪 SELLER SIDE SCREENS

### 1. **Returns List Screen** (`seller_returns_screen.dart`)

**Features:**
- ✅ Shows all return requests
- ✅ Filter chips (All/Pending/Approved/Rejected)
- ✅ Color-coded status badges
- ✅ Approve/Reject buttons for pending
- ✅ Pull to refresh

**Card Layout:**
```
┌─────────────────────────────────────┐
│ Baby Shoes               [PENDING]  │
│ Order #456                          │
├─────────────────────────────────────┤
│ Buyer: Juan Dela Cruz              │
│ Reason: Item damaged                │
│ Refund Amount: ₱450.00             │
│ Details: The shoes have a tear...   │
├─────────────────────────────────────┤
│ [Approve]          [Reject]         │
└─────────────────────────────────────┘
```

**After Approval:**
```
┌─────────────────────────────────────┐
│ Baby Shoes              [APPROVED]  │
│ Order #456                          │
├─────────────────────────────────────┤
│ Buyer: Juan Dela Cruz              │
│ Reason: Item damaged                │
│ Refund Amount: ₱450.00             │
├─────────────────────────────────────┤
│ ✅ Return approved. Item is now     │
│    refunded and moved to Returns    │
│    tab.                             │
└─────────────────────────────────────┘
```

**After Rejection:**
```
┌─────────────────────────────────────┐
│ Baby Shoes              [REJECTED]  │
│ Order #456                          │
├─────────────────────────────────────┤
│ Buyer: Juan Dela Cruz              │
│ Reason: Item damaged                │
│ Refund Amount: ₱450.00             │
├─────────────────────────────────────┤
│ ❌ Rejection Reason:                │
│    Item shows signs of use beyond   │
│    normal wear.                     │
└─────────────────────────────────────┘
```

---

## 🔄 SYNCHRONIZED FLOW

### Step 1: Buyer Submits Return
```
BUYER SIDE:
┌─────────────────────────────────────┐
│ Return #123              [PENDING]  │
│ ⏰ Waiting for seller to review     │
└─────────────────────────────────────┘

SELLER SIDE:
┌─────────────────────────────────────┐
│ Baby Shoes               [PENDING]  │
│ [Approve]          [Reject]         │
└─────────────────────────────────────┘
```

### Step 2A: Seller Approves
```
SELLER ACTION:
Taps [Approve] → Confirmation Dialog → Confirms

SELLER SEES:
┌─────────────────────────────────────┐
│ Baby Shoes              [APPROVED]  │
│ ✅ Return approved. Item is now     │
│    refunded and moved to Returns    │
│    tab.                             │
└─────────────────────────────────────┘

BUYER SEES:
┌─────────────────────────────────────┐
│ Return #123             [APPROVED]  │
│ ✅ Your return request was approved.│
│    The item is now refunded.        │
└─────────────────────────────────────┘

DATABASE:
- return_request.status = 'approved'
- order.status = 'refunded'
```

### Step 2B: Seller Rejects
```
SELLER ACTION:
Taps [Reject] → Enter Reason → Confirms

SELLER SEES:
┌─────────────────────────────────────┐
│ Baby Shoes              [REJECTED]  │
│ ❌ Rejection Reason:                │
│    Item shows signs of use...       │
└─────────────────────────────────────┘

BUYER SEES:
┌─────────────────────────────────────┐
│ Return #123             [REJECTED]  │
│ ❌ Your return request was rejected │
│    by the seller.                   │
└─────────────────────────────────────┘

DATABASE:
- return_request.status = 'rejected'
- return_request.seller_response_reason = 'Item shows...'
```

---

## 🎨 UI CONSISTENCY

### Card Design (Both Sides)
```
✅ Same border radius: 12px
✅ Same elevation: 2
✅ Same padding: 16px
✅ Same status badge style
✅ Same color scheme
```

### Status Badge (Both Sides)
```
✅ Rounded corners: 20px
✅ Border width: 1.5px
✅ Padding: 12px horizontal, 6px vertical
✅ Bold text: 12px
✅ Same colors for same status
```

### Status Messages (Both Sides)
```
✅ Same padding: 12px
✅ Same border radius: 8px
✅ Same icon size: 18px
✅ Same text size: 12px
✅ Same background colors
```

---

## 📊 DATA STRUCTURE (Synchronized)

### Return Request Object
```dart
{
  'id': 123,
  'order_id': 456,
  'product_name': 'Baby Shoes',
  'buyer_name': 'Juan Dela Cruz',
  'reason': 'Item damaged or defective',
  'description': 'The baby shoes have a tear...',
  'refund_amount': 450.00,
  'status': 'submitted',  // or 'approved', 'rejected'
  'seller_response_reason': null,  // filled when rejected
  'created_at': '2025-01-15T10:30:00',
  'processed_at': null,  // filled when approved/rejected
}
```

---

## 🔔 NOTIFICATIONS (Synchronized)

### When Buyer Submits:
```
SELLER RECEIVES:
🔔 New Return Request
   Order #456 - Baby Shoes
   Reason: Item damaged or defective
   Tap to review →
```

### When Seller Approves:
```
BUYER RECEIVES:
🔔 Return Approved
   Your return request for Order #456 
   has been approved. The item is now 
   refunded.
```

### When Seller Rejects:
```
BUYER RECEIVES:
🔔 Return Rejected
   Your return request for Order #456 
   was rejected.
   Reason: Item shows signs of use...
```

---

## ✅ VALIDATION & ERROR HANDLING

### Buyer Side:
```dart
✅ Must select at least 1 item
✅ Reason is required
✅ Photos are optional (max 5)
✅ Show loading state during submission
✅ Show error if API fails
✅ Show success message after submission
```

### Seller Side:
```dart
✅ Show confirmation before approve
✅ Require reason for rejection
✅ Validate rejection reason not empty
✅ Show loading state during action
✅ Show error if API fails
✅ Show success message after action
✅ Refresh list after action
```

---

## 🚀 API ENDPOINTS (Synchronized)

### Buyer Endpoints:
```
POST   /api/buyer/orders/:id/return-request
GET    /api/buyer/return-requests
```

### Seller Endpoints:
```
GET    /api/seller/return-requests
POST   /api/seller/return-requests/:id/approve
POST   /api/seller/return-requests/:id/reject
```

### Response Format (Same for Both):
```json
{
  "success": true,
  "message": "Return approved. Item is now refunded.",
  "return_request": {
    "id": 123,
    "status": "approved",
    "order_status": "refunded"
  }
}
```

---

## 🎯 KEY IMPROVEMENTS

### Before:
```
❌ Different status labels
❌ Different colors
❌ Different messages
❌ Inconsistent UI
❌ Confusing for users
```

### After:
```
✅ Same status labels
✅ Same colors
✅ Same messages
✅ Consistent UI
✅ Clear for users
✅ No confusion
✅ Professional look
```

---

## 📝 TESTING CHECKLIST

### Buyer Side:
- [ ] Can submit return request
- [ ] See PENDING status with orange badge
- [ ] See "Waiting for seller" message
- [ ] Receive notification when approved
- [ ] See APPROVED status with green badge
- [ ] See "Item is now refunded" message
- [ ] Receive notification when rejected
- [ ] See REJECTED status with red badge
- [ ] See rejection message

### Seller Side:
- [ ] Receive notification for new return
- [ ] See return in list with PENDING status
- [ ] Can tap Approve button
- [ ] See confirmation dialog
- [ ] See APPROVED status after approval
- [ ] See success message
- [ ] Can tap Reject button
- [ ] See rejection reason dialog
- [ ] Must enter reason to reject
- [ ] See REJECTED status after rejection
- [ ] See rejection reason displayed

### Synchronization:
- [ ] Buyer and seller see same status
- [ ] Buyer and seller see same colors
- [ ] Messages are consistent
- [ ] Real-time updates work
- [ ] No data mismatch
- [ ] No UI inconsistencies

---

## 🎉 SUMMARY

**TUGMA NA ANG LAHAT!**

✅ **Buyer Side:**
- Returns list with status messages
- Color-coded badges
- Clear status indicators

✅ **Seller Side:**
- Returns list with action buttons
- Same color-coded badges
- Same status indicators

✅ **Synchronized:**
- Same status labels
- Same colors
- Same messages
- Same UI design
- No confusion
- Professional look

**WALANG ERROR, WALANG CONFUSION!** 🎊
