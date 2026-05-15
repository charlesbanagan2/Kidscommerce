# Ready-to-Use Backend Code

Copy and paste these into your Flask backend.

---

## 1. Upload Delivery Proof Endpoint

```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import time

@app.route('/api/v1/rider/orders/<int:order_id>/upload-proof', methods=['POST'])
@jwt_required()
def upload_delivery_proof(order_id):
    """Upload delivery proof photo"""
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
        return jsonify({"error": "Invalid file type"}), 400
    
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
    
    # Update order
    order.proof_photo_url = f"/uploads/proofs/{filename}"
    db.session.commit()
    
    return jsonify({
        "success": True,
        "proof_photo_url": order.proof_photo_url
    }), 200
```

---

## 2. Available Orders Endpoint

```python
@app.route('/api/v1/rider/available-orders', methods=['GET'])
@jwt_required()
def get_available_orders():
    """Get orders available for riders to accept"""
    
    # Get orders that need a rider
    available_orders = Order.query.filter(
        Order.rider_id.is_(None),  # No rider assigned
        Order.status.in_(['ready_for_pickup', 'to_ship', 'pending']),
        db.or_(
            Order.payment_status == 'paid',
            Order.payment_method == 'COD'
        )
    ).order_by(Order.created_at.desc()).all()
    
    orders_data = []
    for order in available_orders:
        # Get buyer info
        buyer = User.query.get(order.buyer_id)
        buyer_name = f"{buyer.first_name} {buyer.last_name}" if buyer else "Unknown"
        
        # Get seller info
        seller = User.query.get(order.seller_id) if order.seller_id else None
        seller_name = f"{seller.first_name} {seller.last_name}" if seller else None
        seller_address = seller.address if seller else None
        
        # Get order items
        items_data = []
        for item in order.items:
            product = Product.query.get(item.product_id)
            items_data.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product.name if product else 'Unknown',
                'product_image': product.image_url if product else None,
                'quantity': item.quantity,
                'price': float(item.price),
                'total_price': float(item.quantity * item.price),
                'size': item.size,
                'color': item.color
            })
        
        orders_data.append({
            'id': order.id,
            'buyer_id': order.buyer_id,
            'buyer_name': buyer_name,
            'buyer_email': buyer.email if buyer else None,
            'buyer_phone': buyer.phone if buyer else None,
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
            'seller_name': seller_name,
            'seller_address': seller_address,
            'items': items_data
        })
    
    return jsonify({
        'success': True,
        'count': len(orders_data),
        'orders': orders_data
    }), 200
```

---

## 3. Rider Earnings Endpoint

```python
from datetime import datetime, timedelta

@app.route('/api/rider/earnings', methods=['GET'])
@jwt_required()
def get_rider_earnings():
    """Calculate rider earnings from delivered orders"""
    current_user_id = get_jwt_identity()
    
    # Get all delivered orders for this rider
    delivered_orders = Order.query.filter(
        Order.rider_id == current_user_id,
        Order.status == 'delivered'
    ).all()
    
    # Calculate total earnings
    total_earnings = sum(float(order.shipping_fee) for order in delivered_orders)
    total_deliveries = len(delivered_orders)
    
    # Today's earnings
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = [o for o in delivered_orders 
                   if o.delivered_at and o.delivered_at >= today_start]
    today_earnings = sum(float(order.shipping_fee) for order in today_orders)
    
    # This week's earnings
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_orders = [o for o in delivered_orders 
                  if o.delivered_at and o.delivered_at >= week_start]
    week_earnings = sum(float(order.shipping_fee) for order in week_orders)
    
    # This month's earnings
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_orders = [o for o in delivered_orders 
                   if o.delivered_at and o.delivered_at >= month_start]
    month_earnings = sum(float(order.shipping_fee) for order in month_orders)
    
    # Active deliveries
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

## 4. Mark Order as Delivered Endpoint

```python
@app.route('/api/v1/rider/orders/<int:order_id>/mark-delivered', methods=['POST'])
@jwt_required()
def mark_order_delivered(order_id):
    """Mark order as delivered by rider"""
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

## Database Migration

Run this SQL to add required columns:

```sql
-- Add proof_photo_url column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS proof_photo_url VARCHAR(255);

-- Add delivered_at timestamp
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_rider_status ON orders(rider_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_status_rider ON orders(status, rider_id);
```

---

## App Configuration

Add to your Flask app config:

```python
import os

# Upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directories
os.makedirs(os.path.join(UPLOAD_FOLDER, 'proofs'), exist_ok=True)
```

---

## Testing Commands

Test each endpoint after implementation:

```bash
# 1. Test upload proof
curl -X POST http://localhost:5000/api/v1/rider/orders/22/upload-proof \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "proof_photo=@test.jpg"

# 2. Test available orders
curl http://localhost:5000/api/v1/rider/available-orders \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Test earnings
curl http://localhost:5000/api/rider/earnings \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Test mark delivered
curl -X POST http://localhost:5000/api/v1/rider/orders/22/mark-delivered \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Expected Responses

### Upload Proof:
```json
{
  "success": true,
  "proof_photo_url": "/uploads/proofs/proof_22_1234567890.jpg"
}
```

### Available Orders:
```json
{
  "success": true,
  "count": 2,
  "orders": [...]
}
```

### Earnings:
```json
{
  "success": true,
  "total": 150.00,
  "today": 50.00,
  "week": 100.00,
  "month": 150.00,
  "total_deliveries": 5,
  "active_deliveries": 2
}
```

### Mark Delivered:
```json
{
  "success": true,
  "message": "Order marked as delivered",
  "order_id": 22,
  "delivered_at": "2024-01-05T10:30:00"
}
```

---

## That's It!

Copy these 4 endpoints into your Flask backend, run the SQL migration, and the mobile app will work perfectly! 🚀
