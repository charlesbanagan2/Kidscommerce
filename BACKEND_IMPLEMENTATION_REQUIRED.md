# Backend Implementation Required

## Critical Issues - Mobile App Cannot Function Without These

### 1. Upload Delivery Proof Endpoint (CRITICAL - BLOCKING DELIVERIES)

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Riders cannot complete deliveries  
**Priority:** URGENT

#### Required Endpoint:
```
POST /api/v1/rider/orders/<order_id>/upload-proof
```

#### Implementation:
```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import time

@app.route('/api/v1/rider/orders/<int:order_id>/upload-proof', methods=['POST'])
@jwt_required()
def upload_delivery_proof(order_id):
    """
    Upload delivery proof photo
    - Accepts multipart/form-data with field 'proof_photo'
    - Verifies rider owns this order
    - Saves file to uploads folder
    - Updates order.proof_photo_url in database
    """
    current_user_id = get_jwt_identity()
    
    # Get order and verify rider owns it
    order = Order.query.get_or_404(order_id)
    
    if order.rider_id != current_user_id:
        return jsonify({"error": "Not authorized"}), 403
    
    # Check if file is in request
    if 'proof_photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400
    
    file = request.files['proof_photo']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "Invalid file type. Only JPG, JPEG, PNG allowed"}), 400
    
    # Generate unique filename
    timestamp = int(time.time())
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"proof_{order_id}_{timestamp}.{ext}")
    
    # Ensure upload directory exists
    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'proofs')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Update order with proof photo URL
    order.proof_photo_url = f"/uploads/proofs/{filename}"
    db.session.commit()
    
    return jsonify({
        "success": True,
        "proof_photo_url": order.proof_photo_url,
        "message": "Proof photo uploaded successfully"
    }), 200
```

#### Database Schema Required:
```sql
-- Add column to orders table if not exists
ALTER TABLE orders ADD COLUMN proof_photo_url VARCHAR(255);
```

---

### 2. Available Orders Endpoint (CRITICAL - NO ORDERS SHOWING)

**Status:** ❌ RETURNS EMPTY ARRAY  
**Impact:** Riders cannot see orders to accept  
**Priority:** URGENT

#### Current Issue:
```
GET /api/v1/rider/available-orders
Returns: {"count": 0, "orders": [], "success": true}
```

#### Required Fix:
```python
@app.route('/api/v1/rider/available-orders', methods=['GET'])
@jwt_required()
def get_available_orders():
    """
    Get orders available for riders to accept
    - Orders that are ready for pickup
    - Orders without assigned rider
    - Paid orders only
    """
    # Get orders that need a rider
    available_orders = Order.query.filter(
        Order.rider_id.is_(None),  # No rider assigned
        Order.status.in_(['ready_for_pickup', 'to_ship', 'pending']),  # Ready statuses
        Order.payment_status == 'paid'  # Only paid orders (or COD)
    ).order_by(Order.created_at.desc()).all()
    
    # Also include COD orders
    cod_orders = Order.query.filter(
        Order.rider_id.is_(None),
        Order.status.in_(['ready_for_pickup', 'to_ship', 'pending']),
        Order.payment_method == 'COD'
    ).order_by(Order.created_at.desc()).all()
    
    # Combine and deduplicate
    all_orders = list(set(available_orders + cod_orders))
    
    orders_data = []
    for order in all_orders:
        orders_data.append({
            'id': order.id,
            'buyer_id': order.buyer_id,
            'buyer_name': f"{order.buyer.first_name} {order.buyer.last_name}",
            'buyer_email': order.buyer.email,
            'buyer_phone': order.buyer.phone,
            'status': order.status,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'total_amount': float(order.total_amount),
            'shipping_fee': float(order.shipping_fee),
            'shipping_address': order.shipping_address,
            'recipient_name': order.recipient_name,
            'recipient_phone': order.recipient_phone,
            'notes': order.notes,
            'created_at': order.created_at.isoformat(),
            'seller_name': f"{order.seller.first_name} {order.seller.last_name}" if order.seller else None,
            'seller_address': order.seller.address if order.seller else None,
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'product_image': item.product.image_url,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total_price': float(item.quantity * item.price),
                    'size': item.size,
                    'color': item.color
                }
                for item in order.items
            ]
        })
    
    return jsonify({
        'success': True,
        'count': len(orders_data),
        'orders': orders_data
    }), 200
```

---

### 3. Rider Earnings Endpoint (SHOWING ALL ZEROS)

**Status:** ❌ RETURNS ALL ZEROS  
**Impact:** Riders cannot see their earnings  
**Priority:** HIGH

#### Current Issue:
```
GET /api/rider/earnings
Returns: {
  "active_deliveries": 0,
  "month": 0.0,
  "today": 0.0,
  "total": 0.0,
  "total_deliveries": 0,
  "week": 0.0
}
```

#### Required Fix:
```python
from datetime import datetime, timedelta
from sqlalchemy import func

@app.route('/api/rider/earnings', methods=['GET'])
@jwt_required()
def get_rider_earnings():
    """
    Calculate rider earnings from delivered orders
    """
    current_user_id = get_jwt_identity()
    
    # Get all delivered orders for this rider
    delivered_orders = Order.query.filter(
        Order.rider_id == current_user_id,
        Order.status == 'delivered'
    ).all()
    
    # Calculate total earnings (sum of shipping fees)
    total_earnings = sum(float(order.shipping_fee) for order in delivered_orders)
    total_deliveries = len(delivered_orders)
    
    # Today's earnings
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = [o for o in delivered_orders if o.delivered_at and o.delivered_at >= today_start]
    today_earnings = sum(float(order.shipping_fee) for order in today_orders)
    
    # This week's earnings
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_orders = [o for o in delivered_orders if o.delivered_at and o.delivered_at >= week_start]
    week_earnings = sum(float(order.shipping_fee) for order in week_orders)
    
    # This month's earnings
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_orders = [o for o in delivered_orders if o.delivered_at and o.delivered_at >= month_start]
    month_earnings = sum(float(order.shipping_fee) for order in month_orders)
    
    # Active deliveries (in_transit or to_ship)
    active_deliveries = Order.query.filter(
        Order.rider_id == current_user_id,
        Order.status.in_(['in_transit', 'to_ship'])
    ).count()
    
    return jsonify({
        'success': True,
        'total': total_earnings,
        'today': today_earnings,
        'week': week_earnings,
        'month': month_earnings,
        'total_deliveries': total_deliveries,
        'active_deliveries': active_deliveries
    }), 200
```

---

### 4. Mark Order as Delivered Endpoint

**Status:** ⚠️ NEEDS VERIFICATION  
**Impact:** Cannot complete delivery flow  
**Priority:** HIGH

#### Verify This Endpoint Exists:
```
POST /api/v1/rider/orders/<order_id>/mark-delivered
```

#### Required Implementation:
```python
@app.route('/api/v1/rider/orders/<int:order_id>/mark-delivered', methods=['POST'])
@jwt_required()
def mark_order_delivered(order_id):
    """
    Mark order as delivered by rider
    """
    current_user_id = get_jwt_identity()
    
    order = Order.query.get_or_404(order_id)
    
    # Verify rider owns this order
    if order.rider_id != current_user_id:
        return jsonify({"error": "Not authorized"}), 403
    
    # Verify order is in transit
    if order.status != 'in_transit':
        return jsonify({"error": "Order is not in transit"}), 400
    
    # Update order status
    order.status = 'delivered'
    order.delivered_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Order marked as delivered',
        'order_id': order.id,
        'delivered_at': order.delivered_at.isoformat()
    }), 200
```

---

## Testing Checklist

### After implementing the above:

1. **Test Upload Proof:**
   ```bash
   curl -X POST http://localhost:5000/api/v1/rider/orders/22/upload-proof \
     -H "Authorization: Bearer <token>" \
     -F "proof_photo=@test_image.jpg"
   ```
   Expected: `{"success": true, "proof_photo_url": "/uploads/proofs/proof_22_xxx.jpg"}`

2. **Test Available Orders:**
   ```bash
   curl http://localhost:5000/api/v1/rider/available-orders \
     -H "Authorization: Bearer <token>"
   ```
   Expected: `{"success": true, "count": X, "orders": [...]}`

3. **Test Earnings:**
   ```bash
   curl http://localhost:5000/api/rider/earnings \
     -H "Authorization: Bearer <token>"
   ```
   Expected: Non-zero values if rider has delivered orders

4. **Test Mark Delivered:**
   ```bash
   curl -X POST http://localhost:5000/api/v1/rider/orders/22/mark-delivered \
     -H "Authorization: Bearer <token>"
   ```
   Expected: `{"success": true, "message": "Order marked as delivered"}`

---

## Database Schema Updates Required

```sql
-- 1. Add proof_photo_url column if not exists
ALTER TABLE orders ADD COLUMN IF NOT EXISTS proof_photo_url VARCHAR(255);

-- 2. Add delivered_at timestamp if not exists
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;

-- 3. Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_orders_rider_status ON orders(rider_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_status_rider ON orders(status, rider_id);

-- 4. Verify orders table has these columns:
-- - rider_id (INT, nullable, foreign key to users)
-- - status (VARCHAR: pending, to_ship, in_transit, delivered, etc.)
-- - payment_status (VARCHAR: pending, paid, failed)
-- - payment_method (VARCHAR: COD, card, etc.)
-- - shipping_fee (DECIMAL)
-- - shipping_address (TEXT)
-- - recipient_name (VARCHAR)
-- - recipient_phone (VARCHAR)
-- - notes (TEXT, nullable)
-- - created_at (TIMESTAMP)
-- - delivered_at (TIMESTAMP, nullable)
-- - proof_photo_url (VARCHAR, nullable)
```

---

## File Upload Configuration

Add to your Flask app configuration:

```python
import os

# Upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directories
os.makedirs(os.path.join(UPLOAD_FOLDER, 'proofs'), exist_ok=True)
```

---

## Summary

**Mobile App Status:** ✅ READY - All features implemented and tested  
**Backend Status:** ❌ MISSING CRITICAL ENDPOINTS

**What Works:**
- ✅ Rider login
- ✅ View active deliveries
- ✅ Take delivery proof photo
- ✅ Photo upload attempt with fallback
- ✅ Mark as delivered (with user confirmation)

**What Doesn't Work (Backend Issues):**
- ❌ Photo upload (no endpoint)
- ❌ Available orders (returns empty)
- ❌ Earnings calculation (returns zeros)

**Action Required:**
Implement the 4 endpoints above to make the system fully functional.
