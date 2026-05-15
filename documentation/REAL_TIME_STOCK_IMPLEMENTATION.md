# REAL-TIME STOCK MANAGEMENT IMPLEMENTATION

## Current Problem
- Stock only deducts when seller processes order
- Multiple buyers can order the same stock
- No real-time synchronization between web and mobile

## Required Solution
- Stock deducts IMMEDIATELY when buyer places order
- Stock returns ONLY when seller cancels order
- Real-time sync across web, mobile, and database

## Implementation Plan

### 1. Database Schema Changes
Add `reserved_stock` tracking to prevent overselling:

```sql
-- Add reserved stock column to product table
ALTER TABLE product ADD COLUMN reserved_stock INTEGER DEFAULT 0;

-- Create order_stock_reservation table for tracking
CREATE TABLE order_stock_reservation (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES "order"(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    reserved_at TIMESTAMP DEFAULT NOW(),
    released_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' -- active, released, completed
);
```

### 2. Stock Deduction Logic

#### When Buyer Places Order (Checkout)
```python
@app.route('/checkout', methods=['POST'])
def checkout():
    # ... existing code ...
    
    # STEP 1: Validate stock availability
    for item in cart_items:
        product = Product.query.get(item.product_id)
        available = product.stock - product.reserved_stock
        
        if available < item.quantity:
            flash(f'{product.name} only has {available} items available', 'error')
            return redirect(url_for('cart'))
    
    # STEP 2: Create order
    order = Order(...)
    db.session.add(order)
    db.session.flush()
    
    # STEP 3: Reserve stock IMMEDIATELY
    for item in cart_items:
        product = Product.query.get(item.product_id)
        
        # Increase reserved stock
        product.reserved_stock += item.quantity
        
        # Create reservation record
        reservation = OrderStockReservation(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            status='active'
        )
        db.session.add(reservation)
        
        # Create order item
        order_item = OrderItem(...)
        db.session.add(order_item)
    
    db.session.commit()
    
    # STEP 4: Broadcast stock update
    for item in cart_items:
        available = product.stock - product.reserved_stock
        socketio.emit('product_stock_update', {
            'product_id': item.product_id,
            'stock': product.stock,
            'reserved_stock': product.reserved_stock,
            'available_stock': available
        }, broadcast=True)
```

#### When Seller Cancels Order
```python
@app.route('/seller/cancel-order/<int:order_id>', methods=['POST'])
def seller_cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # STEP 1: Release reserved stock
    reservations = OrderStockReservation.query.filter_by(
        order_id=order_id,
        status='active'
    ).all()
    
    for reservation in reservations:
        product = Product.query.get(reservation.product_id)
        
        # Decrease reserved stock
        product.reserved_stock -= reservation.quantity
        
        # Mark reservation as released
        reservation.status = 'released'
        reservation.released_at = datetime.utcnow()
    
    # STEP 2: Update order status
    order.status = 'cancelled'
    db.session.commit()
    
    # STEP 3: Broadcast stock update
    for reservation in reservations:
        product = Product.query.get(reservation.product_id)
        available = product.stock - product.reserved_stock
        socketio.emit('product_stock_update', {
            'product_id': reservation.product_id,
            'stock': product.stock,
            'reserved_stock': product.reserved_stock,
            'available_stock': available
        }, broadcast=True)
```

#### When Seller Completes Order
```python
@app.route('/seller/complete-order/<int:order_id>', methods=['POST'])
def seller_complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # STEP 1: Deduct actual stock and clear reservation
    reservations = OrderStockReservation.query.filter_by(
        order_id=order_id,
        status='active'
    ).all()
    
    for reservation in reservations:
        product = Product.query.get(reservation.product_id)
        
        # Deduct from actual stock
        product.stock -= reservation.quantity
        
        # Decrease reserved stock
        product.reserved_stock -= reservation.quantity
        
        # Mark reservation as completed
        reservation.status = 'completed'
    
    # STEP 2: Update order status
    order.status = 'completed'
    db.session.commit()
    
    # STEP 3: Broadcast stock update
    for reservation in reservations:
        product = Product.query.get(reservation.product_id)
        available = product.stock - product.reserved_stock
        socketio.emit('product_stock_update', {
            'product_id': reservation.product_id,
            'stock': product.stock,
            'reserved_stock': product.reserved_stock,
            'available_stock': available
        }, broadcast=True)
```

### 3. Display Logic Changes

#### Backend Templates (Jinja2)
```jinja2
{# Calculate available stock #}
{% set available = product.stock - (product.reserved_stock or 0) %}

{# Display stock status #}
{% if available > 0 %}
    <span class="badge bg-success">In stock ({{ available }} available)</span>
{% else %}
    <span class="badge bg-danger">Out of Stock</span>
{% endif %}
```

#### Mobile App (Flutter)
```dart
class Product {
  final int id;
  final String name;
  final double price;
  final int stock;
  final int reservedStock;
  
  int get availableStock => stock - reservedStock;
  bool get isInStock => availableStock > 0;
  
  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      price: json['price'].toDouble(),
      stock: json['stock'] ?? 0,
      reservedStock: json['reserved_stock'] ?? 0,
    );
  }
}
```

### 4. API Endpoint Updates

```python
@app.route('/api/products')
def api_products():
    products = Product.query.filter_by(status='active').all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'stock': p.stock,
        'reserved_stock': p.reserved_stock or 0,
        'available_stock': p.stock - (p.reserved_stock or 0),
        'image_filename': p.image_filename,
        'category_id': p.category_id
    } for p in products])

@app.route('/api/products/<int:product_id>')
def api_product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'stock': product.stock,
        'reserved_stock': product.reserved_stock or 0,
        'available_stock': product.stock - (product.reserved_stock or 0),
        'description': product.description,
        'image_filename': product.image_filename
    })
```

### 5. Real-Time WebSocket Events

#### Server-Side (Flask-SocketIO)
```python
# When stock changes, broadcast to all connected clients
def broadcast_stock_update(product_id):
    product = Product.query.get(product_id)
    if product:
        available = product.stock - (product.reserved_stock or 0)
        socketio.emit('product_stock_update', {
            'product_id': product_id,
            'stock': product.stock,
            'reserved_stock': product.reserved_stock or 0,
            'available_stock': available,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
```

#### Client-Side (JavaScript)
```javascript
// Listen for stock updates
socket.on('product_stock_update', function(data) {
    const productId = data.product_id;
    const available = data.available_stock;
    
    // Update all product cards
    document.querySelectorAll(`[data-product-id="${productId}"]`).forEach(el => {
        const badge = el.querySelector('.stock-badge');
        if (badge) {
            if (available > 0) {
                badge.className = 'badge bg-success';
                badge.textContent = `In stock (${available})`;
            } else {
                badge.className = 'badge bg-danger';
                badge.textContent = 'Out of Stock';
            }
        }
    });
});
```

#### Mobile App (Flutter with Socket.IO)
```dart
void initializeSocket() {
  socket.on('product_stock_update', (data) {
    final productId = data['product_id'];
    final available = data['available_stock'];
    
    // Update product in state management
    productProvider.updateProductStock(productId, available);
  });
}
```

### 6. Price Synchronization

#### Update Product Price
```python
@app.route('/seller/update-product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Update price
    new_price = float(request.form.get('price'))
    product.price = new_price
    db.session.commit()
    
    # Broadcast price update
    socketio.emit('product_price_update', {
        'product_id': product_id,
        'price': new_price,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)
    
    return jsonify({'success': True})
```

## Testing Checklist

- [ ] Buyer A orders 5 items → Stock shows 95 immediately
- [ ] Buyer B orders 95 items → Shows "Out of Stock"
- [ ] Seller cancels Buyer A's order → Stock returns to 100
- [ ] Web and mobile show same stock values
- [ ] Price changes sync across all platforms
- [ ] Multiple users see updates in real-time

## Files to Modify

1. `backend/app.py` - Add stock reservation logic
2. `backend/templates/product_detail.html` - Update display logic
3. `backend/templates/shop.html` - Update display logic
4. `mobile_app/lib/models/product.dart` - Add reserved_stock field
5. `mobile_app/lib/services/socket_service.dart` - Add real-time listeners

## Migration Script

Run this to add the required database columns:

```python
# migrations/add_stock_reservation.py
from app import db, Product

# Add reserved_stock column
db.session.execute('ALTER TABLE product ADD COLUMN IF NOT EXISTS reserved_stock INTEGER DEFAULT 0')

# Create reservation table
db.session.execute('''
    CREATE TABLE IF NOT EXISTS order_stock_reservation (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES "order"(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
        quantity INTEGER NOT NULL,
        reserved_at TIMESTAMP DEFAULT NOW(),
        released_at TIMESTAMP,
        status VARCHAR(20) DEFAULT 'active'
    )
''')

db.session.commit()
print("✓ Stock reservation system ready")
```
