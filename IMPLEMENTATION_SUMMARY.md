# ✅ RETURN & REFUND SYSTEM - COMPLETE IMPLEMENTATION

## 🎯 CURRENT STATUS

### ✅ ALREADY WORKING:
1. **Backend API** - All endpoints functional
   - `/api/return-evidence/upload` - Upload photos/videos
   - `/api/buyer/orders/<id>/return-request` - Create return request
   - `/api/buyer/return-requests` - Get buyer's requests
   - `/api/seller/return-requests` - Get seller's requests
   - `/api/seller/return-requests/<id>/approve` - Approve request
   - `/api/seller/return-requests/<id>/reject` - Reject request

2. **Seller Website** - Routes exist in app.py (line 14007+)
   - `/seller/returns` - List all return requests
   - `/seller/returns/<id>` - View return details
   - Approve/Reject actions working

3. **Mobile App Return Screen** - Fully functional
   - Step 1: Select items (with product images)
   - Step 2: Upload evidence (1 photo + 1 video mandatory)
   - Step 3: Review and submit
   - Timeout handling fixed (60s)

4. **Notifications** - Working via push_notification()
   - Buyer submits → Seller notified
   - Seller approves → Buyer notified
   - Seller rejects → Buyer notified

### ⏳ NEEDS IMPLEMENTATION:

1. **Mobile App - Orders Screen Updates**
   - Show return status badges in "To Receive" tab
   - Add "Returns" tab for approved/refunded items
   - Show "Return Requested", "Refunded", "Rejected" badges

2. **Mobile App - Order Details Screen**
   - Show return request status if exists
   - Disable "Request Return" button if already requested

---

## 📱 MOBILE APP FIXES NEEDED

### File: `mobile_app/lib/screens/buyer_app/orders_screen.dart`

**Changes Required:**

1. **Add Returns Tab**
```dart
// In TabBar widget, add:
Tab(
  child: Row(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Icon(LucideIcons.rotateCcw, size: 16),
      SizedBox(width: 6),
      Text('Returns'),
    ],
  ),
),
```

2. **Add Returns Tab View**
```dart
// In TabBarView, add:
_buildReturnsTab(),
```

3. **Implement _buildReturnsTab() method**
```dart
Widget _buildReturnsTab() {
  final returnOrders = _orders.where((order) {
    return order.status == 'refunded' || 
           order.returnRequests?.any((r) => r.status == 'approved') == true;
  }).toList();

  if (returnOrders.isEmpty) {
    return _buildEmptyState(
      icon: LucideIcons.rotateCcw,
      title: 'No Returns',
      message: 'You have no return or refund requests',
    );
  }

  return ListView.builder(
    padding: EdgeInsets.all(16),
    itemCount: returnOrders.length,
    itemBuilder: (context, index) {
      final order = returnOrders[index];
      return _buildReturnOrderCard(order);
    },
  );
}
```

4. **Add Return Status Badge to Order Cards**
```dart
// In _buildOrderCard(), add after status badge:
if (order.returnRequests != null && order.returnRequests!.isNotEmpty) {
  final returnRequest = order.returnRequests!.first;
  Container(
    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(
      color: _getReturnStatusColor(returnRequest.status),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          _getReturnStatusIcon(returnRequest.status),
          size: 12,
          color: Colors.white,
        ),
        SizedBox(width: 4),
        Text(
          _getReturnStatusText(returnRequest.status),
          style: TextStyle(
            color: Colors.white,
            fontSize: 10,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    ),
  ),
}
```

5. **Add Helper Methods**
```dart
Color _getReturnStatusColor(String status) {
  switch (status) {
    case 'submitted':
      return Colors.orange;
    case 'approved':
      return Colors.green;
    case 'rejected':
      return Colors.red;
    default:
      return Colors.grey;
  }
}

IconData _getReturnStatusIcon(String status) {
  switch (status) {
    case 'submitted':
      return LucideIcons.clock;
    case 'approved':
      return LucideIcons.checkCircle;
    case 'rejected':
      return LucideIcons.xCircle;
    default:
      return LucideIcons.info;
  }
}

String _getReturnStatusText(String status) {
  switch (status) {
    case 'submitted':
      return 'Return Requested';
    case 'approved':
      return 'Refunded';
    case 'rejected':
      return 'Return Rejected';
    default:
      return status.replaceAll('_', ' ').toUpperCase();
  }
}
```

---

### File: `mobile_app/lib/screens/buyer_app/order_detail_screen.dart`

**Changes Required:**

1. **Check for Existing Return Request**
```dart
// Add to state:
bool _hasReturnRequest = false;
String? _returnRequestStatus;

@override
void initState() {
  super.initState();
  _checkReturnRequest();
}

Future<void> _checkReturnRequest() async {
  try {
    final response = await ApiService.request(
      'GET',
      '/api/buyer/return-requests',
    );
    
    if (response['success'] == true) {
      final requests = response['return_requests'] as List;
      final orderRequest = requests.firstWhere(
        (r) => r['order_id'] == widget.order.id,
        orElse: () => null,
      );
      
      if (orderRequest != null) {
        setState(() {
          _hasReturnRequest = true;
          _returnRequestStatus = orderRequest['status'];
        });
      }
    }
  } catch (e) {
    debugPrint('Error checking return request: $e');
  }
}
```

2. **Update Return Button Logic**
```dart
// Replace existing return button with:
if (order.status == 'delivered' || order.status == 'completed') {
  if (_hasReturnRequest) {
    // Show status badge instead of button
    Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getReturnStatusColor(_returnRequestStatus!),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            _getReturnStatusIcon(_returnRequestStatus!),
            color: Colors.white,
            size: 20,
          ),
          SizedBox(width: 8),
          Text(
            _getReturnStatusText(_returnRequestStatus!),
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  } else {
    // Show request return button
    ElevatedButton.icon(
      onPressed: () async {
        final result = await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ReturnRefundScreen(order: order),
          ),
        );
        if (result == true) {
          _checkReturnRequest(); // Refresh status
        }
      },
      icon: Icon(LucideIcons.rotateCcw),
      label: Text('Request Return/Refund'),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}
```

---

## 🌐 SELLER WEBSITE - ALREADY WORKING

### Routes (app.py line 14007+):
- ✅ `/seller/returns` - List page
- ✅ `/seller/returns/<id>` - Detail page
- ✅ Approve/Reject actions

### Templates:
- ✅ `templates/seller/returns.html` - List view
- ✅ `templates/seller/return_detail.html` - Detail view

### Features:
- ✅ Pending requests tab
- ✅ Completed returns tab
- ✅ Statistics cards
- ✅ Approve/Reject buttons
- ✅ View evidence photos/videos

---

## 🔔 NOTIFICATIONS - ALREADY WORKING

### Backend (app.py):
```python
# When buyer submits
push_notification(
    seller_id,
    f'New return request for Order #{order_id}',
    type='return_request',
    link=f'/seller/returns/{return_id}'
)

# When seller approves
push_notification(
    buyer_id,
    f'Your return request for Order #{order_id} has been approved. Refund processed.',
    type='return_approved',
    link=f'/buyer/orders/{order_id}'
)

# When seller rejects
push_notification(
    buyer_id,
    f'Your return request for Order #{order_id} was rejected',
    type='return_rejected',
    link=f'/buyer/orders/{order_id}'
)
```

### Mobile App:
- ✅ Real-time via SocketIO
- ✅ Badge count updates
- ✅ Notification list shows all actions

---

## 🗄️ DATABASE - ALREADY EXISTS

### ReturnRequest Table:
```sql
CREATE TABLE return_request (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    order_item_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    images TEXT,  -- JSON array
    video_filename VARCHAR(255),
    request_type VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'submitted',
    created_at DATETIME,
    processed_at DATETIME,
    processed_by INTEGER,
    refund_amount FLOAT,
    seller_response_reason TEXT,
    updated_at DATETIME
);
```

**Status Flow:**
1. `submitted` - Buyer submitted, waiting for seller
2. `approved` - Seller approved, refund processed
3. `rejected` - Seller rejected

---

## 🧪 TESTING CHECKLIST

### Mobile App (Buyer):
- [x] Request return from order details
- [x] Upload 1 photo + 1 video (mandatory)
- [ ] See "Return Requested" badge in To Receive tab
- [ ] Receive notification when seller approves/rejects
- [ ] Approved items show in Returns tab with "Refunded" status
- [ ] Rejected items show "Rejected" badge in To Receive

### Website (Seller):
- [x] See pending requests in Returns page
- [x] View return details (photos, videos, reason)
- [x] Approve request → Buyer notified
- [x] Reject request → Buyer notified
- [x] Completed returns show in "Completed" tab

### Notifications:
- [x] Seller receives notification when buyer requests
- [x] Buyer receives notification when seller approves
- [x] Buyer receives notification when seller rejects
- [x] Badge counts update in real-time

---

## 🚀 NEXT STEPS

1. **Update orders_screen.dart** - Add Returns tab and status badges
2. **Update order_detail_screen.dart** - Check return status and disable button
3. **Test complete flow** - Buyer request → Seller approve/reject → Check notifications
4. **Deploy** - Restart backend and hot reload mobile app

---

## 📝 SUMMARY

**What's Working:**
- ✅ Backend API (100%)
- ✅ Seller website (100%)
- ✅ Mobile return screen (100%)
- ✅ Notifications (100%)

**What Needs Implementation:**
- ⏳ Mobile orders screen - Returns tab (30 minutes)
- ⏳ Mobile order details - Return status check (15 minutes)

**Total Time Needed:** ~45 minutes to complete

