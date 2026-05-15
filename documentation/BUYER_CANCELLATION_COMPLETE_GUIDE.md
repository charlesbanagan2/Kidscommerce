# COMPLETE BUYER CANCELLATION FLOW WITH STOCK MANAGEMENT

## Overview

This implements a two-tier cancellation system:

1. **Direct Cancellation** (Before seller processes)
   - Buyer cancels instantly
   - Stock released immediately
   - No seller approval needed

2. **Request Cancellation** (After seller processes)
   - Buyer requests cancellation
   - Seller must approve/reject
   - Stock released only when approved

---

## Complete Flow Examples

### Example 1: Direct Cancellation (Early Stage)

**Initial State:**
- Product A: 100 stock, 0 reserved
- Display: "In stock (100 available)"

**Step 1: Buyer A orders 5 items**
```
Order Status: pending
Database: stock=100, reserved_stock=5
Display: "In stock (95 available)"
```

**Step 2: Buyer B orders 95 items**
```
Order Status: pending
Database: stock=100, reserved_stock=100
Display: "Out of Stock"
```

**Step 3: Buyer B cancels order (Direct - no seller approval needed)**
```
Action: Buyer clicks "Cancel Order"
System: Checks order.status = 'pending' → Direct cancellation allowed
Result: 
  - Order status → 'cancelled'
  - Reserved stock released: 100 - 95 = 5
  - Database: stock=100, reserved_stock=5
  - Display: "In stock (95 available)"
```

**Step 4: Buyer A cancels order (Direct - no seller approval needed)**
```
Action: Buyer clicks "Cancel Order"
System: Checks order.status = 'pending' → Direct cancellation allowed
Result:
  - Order status → 'cancelled'
  - Reserved stock released: 5 - 5 = 0
  - Database: stock=100, reserved_stock=0
  - Display: "In stock (100 available)"
```

**Final State:**
- Product A: 100 stock, 0 reserved
- Display: "In stock (100 available)"
- Both orders cancelled, all stock returned

---

### Example 2: Request Cancellation (After Processing)

**Initial State:**
- Product A: 100 stock, 0 reserved

**Step 1: Buyer A orders 5 items**
```
Order Status: pending
Database: stock=100, reserved_stock=5
Display: "In stock (95 available)"
```

**Step 2: Seller processes order**
```
Action: Seller clicks "Process Order"
Order Status: processing
Database: stock=100, reserved_stock=5 (still reserved)
Display: "In stock (95 available)"
```

**Step 3: Buyer A tries to cancel (Requires seller approval)**
```
Action: Buyer clicks "Cancel Order"
System: Checks order.status = 'processing' → Request cancellation
Result:
  - Order status → 'cancellation_requested'
  - Stock STILL RESERVED (not released yet)
  - Database: stock=100, reserved_stock=5
  - Display: "In stock (95 available)"
  - Notification sent to seller
```

**Step 4a: Seller APPROVES cancellation**
```
Action: Seller clicks "Approve Cancellation"
Result:
  - Order status → 'cancelled'
  - Reserved stock released: 5 - 5 = 0
  - Database: stock=100, reserved_stock=0
  - Display: "In stock (100 available)"
  - Notification sent to buyer: "Cancellation approved"
```

**Step 4b: Seller REJECTS cancellation**
```
Action: Seller clicks "Reject Cancellation"
Result:
  - Order status → 'processing' (back to original)
  - Stock REMAINS RESERVED
  - Database: stock=100, reserved_stock=5
  - Display: "In stock (95 available)"
  - Notification sent to buyer: "Cancellation rejected"
```

---

## Order Status Flow

```
┌─────────┐
│ pending │ ──────────────────────────────┐
└─────────┘                                │
     │                                     │
     │ Seller processes                   │ Buyer cancels
     ▼                                     │ (Direct)
┌────────────┐                             │
│ processing │ ─────────────────────┐      │
└────────────┘                      │      │
     │                              │      │
     │ Ready for pickup             │      │
     ▼                              │      │
┌──────────────────┐                │      │
│ ready_for_pickup │                │      │
└──────────────────┘                │      │
     │                              │      │
     │ Rider accepts                │      │
     ▼                              │      │
┌────────────┐                      │      │
│ in_transit │                      │      │
└────────────┘                      │      │
     │                              │      │
     │ Delivered                    │      │
     ▼                              │      │
┌───────────┐                       │      │
│ delivered │                       │      │
└───────────┘                       │      │
     │                              │      │
     │ Buyer confirms               │      │
     ▼                              │      │
┌───────────┐                       │      │
│ completed │                       │      │
└───────────┘                       │      │
                                    │      │
     Buyer requests cancellation    │      │
     (After processing)              │      │
                ▼                    │      │
     ┌────────────────────────┐     │      │
     │ cancellation_requested │     │      │
     └────────────────────────┘     │      │
                │                    │      │
       ┌────────┴────────┐           │      │
       │                 │           │      │
  Seller approves   Seller rejects   │      │
       │                 │           │      │
       ▼                 ▼           │      │
  ┌───────────┐    ┌────────────┐   │      │
  │ cancelled │◄───│ processing │   │      │
  └───────────┘    └────────────┘   │      │
       ▲                             │      │
       └─────────────────────────────┴──────┘
```

---

## Database Schema

### Order Table
```sql
CREATE TABLE "order" (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER REFERENCES "user"(id),
    status VARCHAR(50) DEFAULT 'pending',
    -- Status values:
    -- 'pending' - Order placed, not processed
    -- 'to_pay' - Awaiting payment
    -- 'processing' - Seller is processing
    -- 'ready_for_pickup' - Ready for rider
    -- 'in_transit' - Rider delivering
    -- 'delivered' - Delivered to buyer
    -- 'completed' - Buyer confirmed receipt
    -- 'cancellation_requested' - Buyer wants to cancel
    -- 'cancelled' - Order cancelled
    
    return_reason TEXT,  -- Cancellation reason
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Order Stock Reservation Table
```sql
CREATE TABLE order_stock_reservation (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES "order"(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    reserved_at TIMESTAMP DEFAULT NOW(),
    released_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    -- Status values:
    -- 'active' - Stock is reserved
    -- 'released' - Stock released (order cancelled)
    -- 'completed' - Stock deducted (order completed)
);
```

---

## Web UI Updates

### Buyer Order Detail Page

Add cancellation button with conditional logic:

```html
{% if order.status in ['pending', 'to_pay'] %}
    <!-- Direct cancellation -->
    <a href="{{ url_for('cancel_order', order_id=order.id) }}" 
       class="btn btn-danger">
        <i class="fas fa-times-circle me-2"></i>Cancel Order
    </a>
    <small class="text-muted d-block mt-1">
        You can cancel this order directly
    </small>

{% elif order.status in ['processing', 'ready_for_pickup', 'in_transit'] %}
    <!-- Request cancellation -->
    <a href="{{ url_for('cancel_order', order_id=order.id) }}" 
       class="btn btn-warning">
        <i class="fas fa-exclamation-circle me-2"></i>Request Cancellation
    </a>
    <small class="text-muted d-block mt-1">
        Seller approval required
    </small>

{% elif order.status == 'cancellation_requested' %}
    <!-- Pending seller approval -->
    <div class="alert alert-info">
        <i class="fas fa-clock me-2"></i>
        Cancellation request pending seller approval
    </div>

{% elif order.status == 'cancelled' %}
    <!-- Already cancelled -->
    <div class="alert alert-secondary">
        <i class="fas fa-ban me-2"></i>
        Order cancelled
    </div>

{% elif order.status in ['delivered', 'completed'] %}
    <!-- Cannot cancel -->
    <small class="text-muted">
        This order cannot be cancelled
    </small>
{% endif %}
```

### Seller Order Detail Page

Add cancellation approval buttons:

```html
{% if order.status == 'cancellation_requested' %}
<div class="card border-warning mb-3">
    <div class="card-header bg-warning text-dark">
        <i class="fas fa-exclamation-triangle me-2"></i>
        Cancellation Request
    </div>
    <div class="card-body">
        <p><strong>Buyer Reason:</strong> {{ order.return_reason }}</p>
        
        <form method="POST" action="{{ url_for('seller_approve_cancellation', order_id=order.id) }}" 
              class="d-inline">
            <button type="submit" class="btn btn-success">
                <i class="fas fa-check me-2"></i>Approve Cancellation
            </button>
        </form>
        
        <button type="button" class="btn btn-danger" data-bs-toggle="modal" 
                data-bs-target="#rejectModal">
            <i class="fas fa-times me-2"></i>Reject Cancellation
        </button>
    </div>
</div>

<!-- Rejection Modal -->
<div class="modal fade" id="rejectModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form method="POST" action="{{ url_for('seller_reject_cancellation', order_id=order.id) }}">
                <div class="modal-header">
                    <h5 class="modal-title">Reject Cancellation</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Reason for rejection:</label>
                        <textarea class="form-control" name="rejection_reason" 
                                  rows="3" required></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" 
                            data-bs-dismiss="modal">Close</button>
                    <button type="submit" class="btn btn-danger">Reject</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endif %}
```

---

## Mobile App Implementation

### Cancel Order Screen (Flutter)

```dart
class CancelOrderScreen extends StatefulWidget {
  final Order order;
  
  const CancelOrderScreen({Key? key, required this.order}) : super(key: key);
  
  @override
  _CancelOrderScreenState createState() => _CancelOrderScreenState();
}

class _CancelOrderScreenState extends State<CancelOrderScreen> {
  final List<String> _selectedReasons = [];
  final TextEditingController _otherReasonController = TextEditingController();
  bool _isLoading = false;
  
  bool get _canDirectCancel => 
      widget.order.status == 'pending' || widget.order.status == 'to_pay';
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Cancel Order #${widget.order.id}'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Warning message
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _canDirectCancel ? Colors.red.shade50 : Colors.orange.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _canDirectCancel ? Colors.red : Colors.orange,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _canDirectCancel ? Icons.warning : Icons.info,
                    color: _canDirectCancel ? Colors.red : Colors.orange,
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _canDirectCancel
                          ? 'This order will be cancelled immediately and stock will be released.'
                          : 'Seller approval required. Stock will be released only if approved.',
                      style: TextStyle(
                        color: _canDirectCancel ? Colors.red.shade900 : Colors.orange.shade900,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 24),
            
            // Cancellation reasons
            Text(
              'Select your reason(s):',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            SizedBox(height: 12),
            
            _buildReasonCheckbox('Ordered by mistake'),
            _buildReasonCheckbox('Change of mind'),
            _buildReasonCheckbox('Found a cheaper alternative'),
            _buildReasonCheckbox('Ordered the wrong item'),
            _buildReasonCheckbox('Seller has not processed my order'),
            
            SizedBox(height: 16),
            
            // Other reason
            TextField(
              controller: _otherReasonController,
              decoration: InputDecoration(
                labelText: 'Other reason (optional)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            
            SizedBox(height: 24),
            
            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Keep Order'),
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submitCancellation,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _canDirectCancel ? Colors.red : Colors.orange,
                    ),
                    child: _isLoading
                        ? SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(_canDirectCancel ? 'Cancel Order' : 'Request Cancellation'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildReasonCheckbox(String reason) {
    return CheckboxListTile(
      title: Text(reason),
      value: _selectedReasons.contains(reason),
      onChanged: (bool? value) {
        setState(() {
          if (value == true) {
            _selectedReasons.add(reason);
          } else {
            _selectedReasons.remove(reason);
          }
        });
      },
      controlAffinity: ListTileControlAffinity.leading,
      contentPadding: EdgeInsets.zero,
    );
  }
  
  Future<void> _submitCancellation() async {
    if (_selectedReasons.isEmpty && _otherReasonController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select at least one reason')),
      );
      return;
    }
    
    setState(() => _isLoading = true);
    
    try {
      final response = await ApiService().cancelOrder(
        widget.order.id,
        reasons: _selectedReasons,
        otherReason: _otherReasonController.text.trim(),
      );
      
      if (response['success']) {
        Navigator.pop(context, true); // Return true to indicate success
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to cancel order: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }
}
```

### API Service Method

```dart
class ApiService {
  Future<Map<String, dynamic>> cancelOrder(
    int orderId, {
    required List<String> reasons,
    String? otherReason,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/orders/$orderId/cancel'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'reasons': reasons,
        'other_reason': otherReason,
      }),
    );
    
    return jsonDecode(response.body);
  }
}
```

---

## Testing Scenarios

### Test 1: Direct Cancellation
1. Place order (status: pending)
2. Check stock: should be reserved
3. Cancel order immediately
4. Check stock: should be released
5. Verify no seller approval needed

### Test 2: Request Cancellation
1. Place order (status: pending)
2. Seller processes order (status: processing)
3. Buyer requests cancellation
4. Check stock: should STILL be reserved
5. Seller approves
6. Check stock: should be released

### Test 3: Rejected Cancellation
1. Place order and seller processes
2. Buyer requests cancellation
3. Seller rejects
4. Check stock: should REMAIN reserved
5. Order continues normally

### Test 4: Multiple Orders
1. Product has 100 stock
2. Buyer A orders 5 (95 available)
3. Buyer B orders 95 (0 available)
4. Buyer B cancels (95 available)
5. Buyer A cancels (100 available)
6. Verify all stock returned

---

## Files to Update

1. ✅ `backend/app.py` - Add routes from `buyer_cancellation_logic.py`
2. ✅ `backend/templates/buyer/order_detail.html` - Add cancel button
3. ✅ `backend/templates/seller/order_detail.html` - Add approval buttons
4. ✅ `mobile_app/lib/screens/cancel_order_screen.dart` - Create screen
5. ✅ `mobile_app/lib/services/api_service.dart` - Add cancel method

---

## Summary

✅ **Direct Cancellation**: Buyer cancels before seller processes → Stock released immediately
✅ **Request Cancellation**: Buyer requests after seller processes → Requires approval
✅ **Stock Management**: Stock only released when cancellation is approved
✅ **Real-Time Sync**: All platforms updated via WebSocket
✅ **Mobile & Web**: Same logic on both platforms
