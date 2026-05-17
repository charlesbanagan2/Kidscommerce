# MOBILE APP CODE FIXES - COPY & PASTE READY

## 📱 File 1: orders_screen.dart - Add Returns Tab

### Step 1: Add to TabBar (around line 200)
```dart
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

### Step 2: Add to TabBarView (around line 250)
```dart
_buildReturnsTab(),
```

### Step 3: Add these methods at the end of _OrdersScreenState class (before closing brace)
```dart
// ============= RETURNS TAB =============

Widget _buildReturnsTab() {
  final returnOrders = _orders.where((order) {
    // Show orders that are refunded or have approved return requests
    return order.status == 'refunded';
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

Widget _buildReturnOrderCard(dynamic order) {
  return Container(
    margin: EdgeInsets.only(bottom: 16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.05),
          blurRadius: 10,
          offset: Offset(0, 4),
        ),
      ],
    ),
    child: InkWell(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => OrderDetailScreen(order: order),
          ),
        );
      },
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(LucideIcons.package, size: 18, color: Color(0xFF1e4db7)),
                    SizedBox(width: 8),
                    Text(
                      'Order #${order.id}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: Color(0xFF1e4db7),
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(LucideIcons.checkCircle, size: 12, color: Colors.green),
                      SizedBox(width: 4),
                      Text(
                        'Refunded',
                        style: TextStyle(
                          color: Colors.green,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 12),
            Divider(height: 1),
            SizedBox(height: 12),
            
            // Items
            ...order.items.take(2).map<Widget>((item) {
              return Padding(
                padding: EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: item.product?.imageUrl != null
                          ? Image.network(
                              item.product.imageUrl!,
                              width: 50,
                              height: 50,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => Container(
                                width: 50,
                                height: 50,
                                color: Colors.grey.shade200,
                                child: Icon(Icons.image, color: Colors.grey),
                              ),
                            )
                          : Container(
                              width: 50,
                              height: 50,
                              color: Colors.grey.shade200,
                              child: Icon(Icons.image, color: Colors.grey),
                            ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.productName,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          SizedBox(height: 4),
                          Text(
                            '₱${item.price.toStringAsFixed(2)} × ${item.quantity}',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
            
            if (order.items.length > 2) ...[
              SizedBox(height: 4),
              Text(
                '+${order.items.length - 2} more items',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey.shade600,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
            
            SizedBox(height: 12),
            Divider(height: 1),
            SizedBox(height: 12),
            
            // Footer
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Refund Amount',
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      '₱${order.totalAmount.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
                Icon(
                  LucideIcons.chevronRight,
                  size: 20,
                  color: Colors.grey.shade400,
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

// ============= RETURN STATUS HELPERS =============

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

## 📱 File 2: order_detail_screen.dart - Add Return Status Check

### Step 1: Add to state variables (around line 30)
```dart
bool _hasReturnRequest = false;
String? _returnRequestStatus;
bool _isCheckingReturn = true;
```

### Step 2: Update initState (around line 50)
```dart
@override
void initState() {
  super.initState();
  _checkReturnRequest();
}
```

### Step 3: Add this method after initState
```dart
Future<void> _checkReturnRequest() async {
  try {
    final response = await ApiService.request(
      'GET',
      '/api/buyer/return-requests',
    );
    
    if (response['success'] == true) {
      final requests = response['return_requests'] as List;
      final orderRequest = requests.firstWhereOrNull(
        (r) => r['order_id'] == widget.order.id,
      );
      
      if (orderRequest != null) {
        if (mounted) {
          setState(() {
            _hasReturnRequest = true;
            _returnRequestStatus = orderRequest['status'];
            _isCheckingReturn = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _isCheckingReturn = false;
          });
        }
      }
    } else {
      if (mounted) {
        setState(() {
          _isCheckingReturn = false;
        });
      }
    }
  } catch (e) {
    debugPrint('Error checking return request: $e');
    if (mounted) {
      setState(() {
        _isCheckingReturn = false;
      });
    }
  }
}
```

### Step 4: Replace the "Request Return" button section (search for "Request Return/Refund")
```dart
// Return/Refund Button (only for delivered/completed orders)
if (order.status == 'delivered' || order.status == 'completed') {
  SizedBox(height: 16),
  if (_isCheckingReturn)
    Center(
      child: CircularProgressIndicator(strokeWidth: 2),
    )
  else if (_hasReturnRequest)
    // Show status badge
    Container(
      width: double.infinity,
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
    )
  else
    // Show request button
    SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ReturnRefundScreen(order: order),
            ),
          );
          if (result == true && mounted) {
            setState(() {
              _isCheckingReturn = true;
            });
            await _checkReturnRequest();
          }
        },
        icon: Icon(LucideIcons.rotateCcw, size: 18),
        label: Text(
          'Request Return/Refund',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.orange,
          foregroundColor: Colors.white,
          padding: EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
      ),
    ),
}
```

### Step 5: Add helper methods at the end of _OrderDetailScreenState class
```dart
// ============= RETURN STATUS HELPERS =============

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

## 🧪 TESTING STEPS

1. **Hot Reload Mobile App**
2. **Test Flow:**
   - Go to Orders → To Receive tab
   - Select a delivered order
   - Click "Request Return/Refund"
   - Upload 1 photo + 1 video
   - Submit request
   - Check: "Return Requested" badge appears
3. **Seller Website:**
   - Go to `/seller/returns`
   - See the pending request
   - Click "Review"
   - Click "Approve"
4. **Back to Mobile App:**
   - Check notification received
   - Go to Orders → Returns tab
   - See the refunded order
   - Status shows "Refunded"

---

## ✅ CHECKLIST

- [ ] Copy Step 1 code to orders_screen.dart
- [ ] Copy Step 2 code to orders_screen.dart
- [ ] Copy Step 3 code to orders_screen.dart
- [ ] Copy Step 1-5 code to order_detail_screen.dart
- [ ] Hot reload app
- [ ] Test complete flow
- [ ] Verify notifications work
- [ ] Check Returns tab shows refunded items

