# COMPLETE RETURN & REFUND SYSTEM - IMPLEMENTATION GUIDE

## ✅ SYSTEM OVERVIEW

### Flow:
1. **Buyer** requests return/refund from mobile app
2. **Seller** reviews request on website (approve/reject)
3. **Status Updates**:
   - `submitted` → Buyer submitted, waiting for seller
   - `approved` → Seller approved, item moves to Returns tab, status = "Refunded"
   - `rejected` → Seller rejected, item stays in To Receive tab, status = "Rejected"
4. **Notifications** sent at each step

---

## 📱 MOBILE APP CHANGES

### 1. Order Screen - Show Return Status

**File**: `mobile_app/lib/screens/buyer_app/orders_screen.dart`

**Changes Needed**:
- In "To Receive" tab, show return request status badge
- If return requested but not processed: Show "Return Requested" badge
- If approved: Move to "Returns" tab with "Refunded" status
- If rejected: Show "Return Rejected" badge

### 2. Order Details - Return Request Button

**File**: `mobile_app/lib/screens/buyer_app/order_detail_screen.dart`

**Changes Needed**:
- Show "Request Return" button only for delivered/completed orders
- If return already requested, show status badge
- Disable button if return already exists

### 3. Returns Tab

**File**: `mobile_app/lib/screens/buyer_app/orders_screen.dart`

**Add New Tab**:
```dart
Tab(text: 'Returns')
```

**Show**:
- All approved return requests
- Status: "Refunded"
- Show refund amount
- Show evidence photos/videos

---

## 🌐 SELLER WEBSITE CHANGES

### 1. Returns Page Route

**File**: `backend/app.py`

**Add Route**:
```python
@app.route('/seller/returns')
@seller_required
def seller_returns():
    seller_id = session['user_id']
    
    # Pending requests (submitted status)
    pending = ReturnRequest.query.filter_by(
        seller_id=seller_id,
        status='submitted'
    ).order_by(ReturnRequest.created_at.desc()).all()
    
    # Completed (approved/rejected)
    completed = ReturnRequest.query.filter_by(
        seller_id=seller_id
    ).filter(
        ReturnRequest.status.in_(['approved', 'rejected', 'refunded'])
    ).order_by(ReturnRequest.updated_at.desc()).all()
    
    return render_template('seller/returns.html',
        requests=pending,
        completed_returns=completed,
        total_requests=len(pending) + len(completed),
        pending_requests=len(pending),
        approved_requests=len([r for r in completed if r.status == 'approved']),
        completed_count=len(completed)
    )
```

### 2. Return Detail Page

**File**: `backend/app.py`

**Add Route**:
```python
@app.route('/seller/returns/<int:return_id>')
@seller_required
def seller_return_detail(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    
    # Verify seller owns this
    if rr.seller_id != session['user_id']:
        abort(403)
    
    return render_template('seller/return_detail.html', return_request=rr)
```

### 3. Approve/Reject Actions

**File**: `backend/app.py`

**Add Routes**:
```python
@app.route('/seller/returns/<int:return_id>/approve', methods=['POST'])
@seller_required
def seller_approve_return(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    
    if rr.seller_id != session['user_id']:
        abort(403)
    
    if rr.status != 'submitted':
        flash('Invalid status', 'error')
        return redirect(url_for('seller_returns'))
    
    # Approve
    rr.status = 'approved'
    rr.processed_at = datetime.utcnow()
    rr.processed_by = session['user_id']
    
    # Update order status to refunded
    order = Order.query.get(rr.order_id)
    if order:
        order.status = 'refunded'
    
    db.session.commit()
    
    # Notify buyer
    push_notification(
        rr.buyer_id,
        f'Your return request for Order #{rr.order_id} has been approved. Refund processed.',
        type='return_approved',
        link=f'/buyer/orders/{rr.order_id}'
    )
    
    flash('Return request approved successfully', 'success')
    return redirect(url_for('seller_returns'))

@app.route('/seller/returns/<int:return_id>/reject', methods=['POST'])
@seller_required
def seller_reject_return(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    
    if rr.seller_id != session['user_id']:
        abort(403)
    
    if rr.status != 'submitted':
        flash('Invalid status', 'error')
        return redirect(url_for('seller_returns'))
    
    reason = request.form.get('reason', '').strip()
    
    # Reject
    rr.status = 'rejected'
    rr.seller_response_reason = reason
    rr.processed_at = datetime.utcnow()
    rr.processed_by = session['user_id']
    db.session.commit()
    
    # Notify buyer
    push_notification(
        rr.buyer_id,
        f'Your return request for Order #{rr.order_id} was rejected',
        type='return_rejected',
        link=f'/buyer/orders/{rr.order_id}'
    )
    
    flash('Return request rejected', 'success')
    return redirect(url_for('seller_returns'))
```

---

## 🔔 NOTIFICATIONS

### Backend Notifications (Already Working)
- ✅ Buyer submits → Seller notified
- ✅ Seller approves → Buyer notified
- ✅ Seller rejects → Buyer notified

### Mobile App Notifications
- ✅ Real-time via SocketIO
- ✅ Badge count updates
- ✅ Notification list shows all actions

---

## 🗄️ DATABASE

### ReturnRequest Table (Already Exists)
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
    images TEXT,  -- JSON array of image URLs
    video_filename VARCHAR(255),
    request_type VARCHAR(20) NOT NULL,  -- 'return' or 'refund'
    status VARCHAR(30) DEFAULT 'submitted',  -- submitted, approved, rejected, refunded
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    processed_by INTEGER,
    refund_amount FLOAT,
    seller_response_reason TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧪 TESTING CHECKLIST

### Mobile App (Buyer)
- [ ] Can request return from order details
- [ ] Upload 1 photo + 1 video (mandatory)
- [ ] See "Return Requested" status in To Receive tab
- [ ] Receive notification when seller approves/rejects
- [ ] Approved items move to Returns tab with "Refunded" status
- [ ] Rejected items stay in To Receive with "Rejected" badge

### Website (Seller)
- [ ] See pending requests in Returns page
- [ ] View return details (photos, videos, reason)
- [ ] Approve request → Item becomes "Refunded"
- [ ] Reject request → Item stays in buyer's To Receive
- [ ] Completed returns show in "Completed" tab

### Notifications
- [ ] Seller receives notification when buyer requests
- [ ] Buyer receives notification when seller approves
- [ ] Buyer receives notification when seller rejects
- [ ] Badge counts update in real-time

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: Token Missing (401)
**Fix**: Already fixed in `api_service.dart` - tokens now persist properly

### Issue 2: Timeout Errors
**Fix**: Increased timeout to 60s for slow connections

### Issue 3: Product Images Not Showing
**Fix**: Use `item.product?.imageUrl` with null safety

### Issue 4: Video Upload Not Working
**Fix**: Added `_pickVideo()` method with `ImagePicker.pickVideo()`

---

## 📝 IMPLEMENTATION STEPS

1. ✅ Backend API endpoints (Already done)
2. ✅ Mobile app return screen (Already done)
3. ⏳ Seller website routes (Need to add)
4. ⏳ Mobile app order screen updates (Need to add)
5. ⏳ Returns tab in mobile app (Need to add)
6. ✅ Notifications (Already working)

---

## 🚀 DEPLOYMENT

1. Restart Flask backend
2. Hot reload mobile app
3. Test complete flow:
   - Buyer requests return
   - Seller approves/rejects
   - Check notifications
   - Verify status updates

