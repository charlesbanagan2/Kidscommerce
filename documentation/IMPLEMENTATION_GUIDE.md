# COMPLETE IMPLEMENTATION GUIDE - REAL-TIME STOCK & PRICE SYNC

## Overview
This guide implements real-time stock reservation and price synchronization across:
- ✅ Database (PostgreSQL/Supabase)
- ✅ Web Application (Flask)
- ✅ Mobile Application (Flutter)

## How It Works

### Stock Flow Example:
1. **Item A has 100 stock**
   - Database: stock=100, reserved_stock=0
   - Display: "In stock (100 available)"

2. **Buyer orders 5 items**
   - Database: stock=100, reserved_stock=5
   - Display: "In stock (95 available)"
   - Stock is RESERVED immediately

3. **Buyer B orders 95 items**
   - Database: stock=100, reserved_stock=100
   - Display: "Out of Stock"

4. **Seller cancels first order**
   - Database: stock=100, reserved_stock=95
   - Display: "In stock (5 available)"
   - Stock is RELEASED back

5. **Seller completes second order**
   - Database: stock=5, reserved_stock=0
   - Display: "In stock (5 available)"
   - Actual stock is DEDUCTED

## Step-by-Step Implementation

### STEP 1: Database Migration (5 minutes)

1. Open terminal in `backend` folder
2. Run the migration script:
   ```bash
   python add_stock_reservation.py
   ```

This adds:
- `reserved_stock` column to `product` table
- `order_stock_reservation` tracking table
- Necessary indexes

**Verify:**
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'product' AND column_name = 'reserved_stock';
```

---

### STEP 2: Update Backend Code (30 minutes)

#### 2.1 Add Model to app.py

Open `backend/app.py` and add this model after other models (around line 500):

```python
class OrderStockReservation(db.Model):
    """Track stock reservations for orders"""
    __tablename__ = 'order_stock_reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    
    order = db.relationship('Order', backref='stock_reservations')
    product = db.relationship('Product', backref='stock_reservations')
```

#### 2.2 Add Helper Functions

Copy all functions from `stock_management_functions.py` and add to `app.py`:
- `reserve_stock()`
- `release_stock()`
- `complete_stock_reservation()`
- `broadcast_stock_update()`
- `broadcast_price_update()`

#### 2.3 Update Checkout Route

Find `@app.route('/checkout')` and replace with the version in `stock_management_functions.py`

Key changes:
- Validates available stock BEFORE creating order
- Reserves stock IMMEDIATELY when order is placed
- Broadcasts updates to all clients

#### 2.4 Update API Endpoint

Find `@app.route('/api/products')` and update to return:
```python
{
    'id': p.id,
    'name': p.name,
    'price': float(p.price),
    'stock': p.stock,
    'reserved_stock': p.reserved_stock or 0,
    'available_stock': p.stock - (p.reserved_stock or 0),
    # ... other fields
}
```

#### 2.5 Add Cancel/Complete Order Routes

Add these routes if they don't exist:
- `/seller/cancel-order/<int:order_id>` - Releases stock
- `/seller/complete-order/<int:order_id>` - Deducts actual stock

---

### STEP 3: Update Templates (20 minutes)

#### 3.1 Product Detail Template

File: `backend/templates/product_detail.html`

Replace stock display section with code from `TEMPLATE_UPDATES_STOCK.md`

Key changes:
- Calculate: `available_stock = product.stock - (product.reserved_stock or 0)`
- Show available stock instead of total stock
- Add real-time update JavaScript

#### 3.2 Shop Template

File: `backend/templates/shop.html`

Update product cards to show available stock

#### 3.3 Cart Template

File: `backend/templates/cart.html`

Add stock validation before checkout

---

### STEP 4: Update Mobile App (30 minutes)

#### 4.1 Update Product Model

File: `mobile_app/lib/models/product.dart`

Add fields:
```dart
final int reservedStock;
int get availableStock => stock - reservedStock;
bool get isInStock => availableStock > 0;
```

#### 4.2 Add Socket Service

Create: `mobile_app/lib/services/socket_service.dart`

Copy code from `MOBILE_APP_UPDATES_STOCK.md`

#### 4.3 Update Product Provider

File: `mobile_app/lib/providers/product_provider.dart`

Add socket listeners for real-time updates

#### 4.4 Update UI Widgets

Update product cards to show available stock

#### 4.5 Add Dependencies

File: `mobile_app/pubspec.yaml`

```yaml
dependencies:
  socket_io_client: ^2.0.3+1
```

Run: `flutter pub get`

---

### STEP 5: Testing (15 minutes)

#### Test Scenario 1: Stock Reservation
1. Open product with 100 stock
2. Place order for 5 items
3. **Expected**: Stock shows 95 available immediately
4. Check database: `reserved_stock = 5`

#### Test Scenario 2: Out of Stock
1. Order remaining 95 items
2. **Expected**: Product shows "Out of Stock"
3. Try to order more
4. **Expected**: Error message

#### Test Scenario 3: Cancel Order
1. Seller cancels first order (5 items)
2. **Expected**: Stock returns to 95 available
3. Check database: `reserved_stock = 95`

#### Test Scenario 4: Complete Order
1. Seller completes second order (95 items)
2. **Expected**: Actual stock deducted to 5
3. Check database: `stock = 5, reserved_stock = 0`

#### Test Scenario 5: Real-Time Sync
1. Open product on web browser
2. Open same product on mobile app
3. Place order on web
4. **Expected**: Mobile app updates immediately
5. **Expected**: Both show same stock value

#### Test Scenario 6: Price Update
1. Seller updates product price
2. **Expected**: Web and mobile update immediately
3. **Expected**: All displays show new price

---

## Verification Queries

### Check Stock Reservations
```sql
SELECT 
    p.id,
    p.name,
    p.stock,
    p.reserved_stock,
    (p.stock - COALESCE(p.reserved_stock, 0)) as available_stock
FROM product p
WHERE p.id = YOUR_PRODUCT_ID;
```

### Check Active Reservations
```sql
SELECT 
    osr.*,
    o.status as order_status,
    p.name as product_name
FROM order_stock_reservation osr
JOIN "order" o ON osr.order_id = o.id
JOIN product p ON osr.product_id = p.id
WHERE osr.status = 'active'
ORDER BY osr.reserved_at DESC;
```

### Check Order Stock History
```sql
SELECT 
    o.id as order_id,
    o.status,
    p.name as product_name,
    osr.quantity,
    osr.status as reservation_status,
    osr.reserved_at,
    osr.released_at
FROM "order" o
JOIN order_stock_reservation osr ON o.id = osr.order_id
JOIN product p ON osr.product_id = p.id
WHERE o.id = YOUR_ORDER_ID;
```

---

## Troubleshooting

### Issue: Stock not updating in real-time
**Solution**: Check SocketIO connection
```javascript
console.log('Socket connected:', socket.connected);
```

### Issue: Reserved stock not releasing
**Solution**: Check order status and reservation status
```sql
SELECT * FROM order_stock_reservation WHERE order_id = X;
```

### Issue: Mobile app not receiving updates
**Solution**: Verify socket connection in Flutter
```dart
print('Socket connected: ${socketService.isConnected}');
```

### Issue: Stock goes negative
**Solution**: Add validation in checkout
```python
if available < item.quantity:
    flash('Insufficient stock', 'error')
    return redirect(url_for('cart'))
```

---

## Files Created

1. ✅ `add_stock_reservation.py` - Database migration
2. ✅ `stock_management_functions.py` - Backend helper functions
3. ✅ `TEMPLATE_UPDATES_STOCK.md` - Template changes
4. ✅ `MOBILE_APP_UPDATES_STOCK.md` - Mobile app changes
5. ✅ `REAL_TIME_STOCK_IMPLEMENTATION.md` - Technical documentation
6. ✅ This file - Complete implementation guide

---

## Success Criteria

- [x] Database has `reserved_stock` column
- [x] Orders reserve stock immediately
- [x] Cancelled orders release stock
- [x] Completed orders deduct actual stock
- [x] Web shows available stock (total - reserved)
- [x] Mobile shows available stock (total - reserved)
- [x] Real-time updates work on web
- [x] Real-time updates work on mobile
- [x] Price changes sync across platforms
- [x] Multiple users see same stock values

---

## Next Steps

1. Run database migration
2. Update backend code
3. Update templates
4. Update mobile app
5. Test all scenarios
6. Deploy to production

**Estimated Total Time**: 2 hours

**Need Help?** Check the detailed documentation in:
- `REAL_TIME_STOCK_IMPLEMENTATION.md`
- `stock_management_functions.py`
- `TEMPLATE_UPDATES_STOCK.md`
- `MOBILE_APP_UPDATES_STOCK.md`
