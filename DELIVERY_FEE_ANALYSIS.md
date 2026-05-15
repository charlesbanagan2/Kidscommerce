# Delivery Fee Visibility and Flow Analysis

## Summary
Nag-check ako ng delivery fee visibility sa buyer checkout screen at rider available orders tab. Narito ang findings:

---

## 1. PROVINCE DELIVERY FEE SYSTEM

### Implementation (province_delivery_fees.py)
```python
PROVINCE_RANKS = {
    'Laguna': 1,  # Base location
    'Rizal': 2,
    'Quezon': 3,
    # ... 82 provinces total
}

BASE_FEE = 36  # pesos per rank

def calculate_delivery_fee(province):
    rank = PROVINCE_RANKS.get(province, 1)
    return rank * BASE_FEE
```

**Formula:** `Delivery Fee = Province Rank × ₱36`

**Examples:**
- Laguna (Rank 1): ₱36
- Rizal (Rank 2): ₱72
- Cebu (Rank 45): ₱1,620
- Tawi-Tawi (Rank 82): ₱2,952

---

## 2. BUYER CHECKOUT SCREEN

### Current Implementation (app.py line 9168-9350)

```python
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # ... cart items loading ...
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    shipping_fee = 50.0  # FIXED SHIPPING FEE
    
    # NO DELIVERY FEE CALCULATION BASED ON PROVINCE!
    
    grand_total = total - discount_amount + shipping_fee
```

### ❌ PROBLEMA #1: Walang Province-Based Delivery Fee sa Checkout

**Current Flow:**
1. Buyer selects address (may province field)
2. System shows FIXED ₱50 shipping fee
3. **HINDI nakikita ang actual delivery fee based sa province**
4. Grand total = Subtotal - Discount + ₱50 (fixed)

**Expected Flow:**
1. Buyer selects address with province
2. System calculates: `delivery_fee = calculate_delivery_fee(province)`
3. Display delivery fee sa checkout summary
4. Grand total = Subtotal - Discount + Delivery Fee

---

## 3. DATABASE SCHEMA

### Order Table (app.py line 1985)
```python
class Order(db.Model):
    # ... other fields ...
    delivery_fee = db.Column(db.Float, default=36.0)  # Province-based delivery fee
    shipping_fee = db.Column(db.Float, default=0.0)
    rider_earnings = db.Column(db.Float, default=0.0)
```

✅ **Database ready** - may delivery_fee column na

---

## 4. RIDER AVAILABLE ORDERS TAB

### Current Implementation (app.py line ~12000+)

```python
@app.route('/rider/orders/available')
@rider_required
def rider_available_orders():
    orders = Order.query.filter_by(status='ready_for_pickup').all()
    
    # Orders data includes:
    # - order.id
    # - order.total_amount
    # - order.buyer info
    # - order.shipping_address
```

### ❌ PROBLEMA #2: Delivery Fee Not Visible sa Rider View

**Current:** Rider sees order total amount lang
**Expected:** Rider should see:
- Order total
- **Delivery fee (their earnings)**
- Pickup address
- Delivery address
- Distance estimate

---

## 5. RIDER EARNINGS FLOW

### Current Implementation (app.py line 2426-2427)

```python
def _release_commissions(order: 'Order'):
    # ... seller/admin commission logic ...
    
    # Rider earnings
    if order.picked_up_by:
        delivery_fee = float(order.delivery_fee) if hasattr(order, 'delivery_fee') and order.delivery_fee else 36.0
        credit_wallet(order.picked_up_by, delivery_fee, 'order_commission', order.id)
```

✅ **Rider earnings = delivery_fee** (province-based)
✅ Released when buyer confirms receipt (status='completed')

---

## 6. API ENDPOINTS

### Mobile Buyer Checkout API (app.py line 18148)

```python
@app.route('/api/v1/buyer/checkout', methods=['POST'])
@token_required
def api_buyer_checkout():
    delivery_fee = float(data.get('delivery_fee', 0.0))  # From client
    
    grand_total = total - discount_amount + shipping_fee + delivery_fee
    
    new_order = Order(
        # ...
        delivery_fee=delivery_fee,
        # ...
    )
```

✅ **Mobile API accepts delivery_fee** from client
❌ **Web checkout HINDI nag-calculate ng delivery_fee**

### Rider Available Orders API (app.py line ~17000+)

```python
@app.route('/api/v1/rider/available-orders')
@token_required
@role_required('rider')
def api_rider_available_orders():
    orders = db.session.query(Order).filter(
        Order.status.in_(['ready_for_pickup', 'to_ship', 'pending']),
        Order.rider_id.is_(None)
    ).all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'total_amount': order.total_amount,
            # ... other fields ...
            'rider_earnings': float(order.get('delivery_fee', 36.0))  # ✅ Included
        })
```

✅ **Mobile API includes rider_earnings (delivery_fee)**
❌ **Web view HINDI nag-display ng delivery_fee**

---

## 7. COMPLETE FLOW ANALYSIS

### Order Creation Flow

```
1. BUYER CHECKOUT
   ├─ Select address (with province)
   ├─ ❌ System uses FIXED ₱50 shipping
   ├─ ❌ NO delivery_fee calculation
   └─ Order created with delivery_fee = 0 or default 36

2. SELLER PROCESSES ORDER
   ├─ Marks as 'processing'
   ├─ Marks as 'ready_for_pickup'
   └─ Order.delivery_fee still not set properly

3. RIDER ACCEPTS ORDER
   ├─ Sees order in available tab
   ├─ ❌ Delivery fee NOT visible (web)
   ├─ ✅ Delivery fee visible (mobile API)
   └─ Accepts order

4. RIDER DELIVERS
   ├─ Marks as 'delivered'
   └─ Waits for buyer confirmation

5. BUYER CONFIRMS
   ├─ Marks as 'completed'
   └─ _release_commissions() called
       ├─ Rider gets: order.delivery_fee
       ├─ Sellers get: 85% of subtotal
       └─ Admins get: 15% of subtotal
```

---

## 8. MISSING LOGIC

### ❌ Checkout Screen (Web)
```python
# MISSING: Province-based delivery fee calculation
# LOCATION: app.py checkout() function

# SHOULD ADD:
from province_delivery_fees import calculate_delivery_fee

# In checkout():
if default_address and default_address.province:
    delivery_fee = calculate_delivery_fee(default_address.province)
else:
    delivery_fee = 36.0  # Default Laguna rate

grand_total = total - discount_amount + delivery_fee
```

### ❌ Order Creation (Web)
```python
# MISSING: Save delivery_fee to order
# LOCATION: app.py checkout() POST handler

# SHOULD ADD:
new_order = Order(
    buyer_id=session['user_id'],
    total_amount=grand_total,
    delivery_fee=delivery_fee,  # ← ADD THIS
    # ... other fields ...
)
```

### ❌ Rider Available Orders (Web)
```python
# MISSING: Display delivery_fee in template
# LOCATION: templates/rider/available_orders.html

# SHOULD DISPLAY:
# - Order #{{ order.id }}
# - Total: ₱{{ order.total_amount }}
# - Your Earnings: ₱{{ order.delivery_fee }}  ← ADD THIS
# - Distance: {{ distance }} km
```

---

## 9. DATABASE VERIFICATION

### Check Current Orders
```sql
SELECT 
    id,
    buyer_id,
    total_amount,
    delivery_fee,
    shipping_fee,
    status,
    shipping_address
FROM "order"
WHERE status IN ('pending', 'ready_for_pickup', 'accepted_by_rider')
ORDER BY created_at DESC
LIMIT 10;
```

### Expected Results:
- ✅ delivery_fee column exists
- ❌ Most orders have delivery_fee = 0 or 36 (default)
- ❌ Should have province-based values (36, 72, 108, etc.)

---

## 10. RECOMMENDATIONS

### Priority 1: Fix Buyer Checkout
1. Import `calculate_delivery_fee` from `province_delivery_fees.py`
2. Get buyer's province from selected address
3. Calculate delivery_fee = province_rank × 36
4. Display delivery fee sa checkout summary
5. Save delivery_fee sa Order table

### Priority 2: Fix Rider Available Orders
1. Display delivery_fee sa web view
2. Show as "Your Earnings: ₱XXX"
3. Include distance estimate
4. Show pickup and delivery addresses

### Priority 3: Update Templates
1. `templates/buyer/checkout.html` - add delivery fee display
2. `templates/rider/available_orders.html` - add earnings display
3. Add province selector with real-time fee calculation

---

## 11. CODE FIXES NEEDED

### File: app.py (checkout function)
```python
# Line ~9170
from province_delivery_fees import calculate_delivery_fee

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # ... existing code ...
    
    # ADD THIS SECTION:
    # Calculate delivery fee based on province
    delivery_fee = 36.0  # Default
    if default_address and default_address.province:
        delivery_fee = calculate_delivery_fee(default_address.province)
    
    # Update grand total calculation
    grand_total = total - discount_amount + delivery_fee
    
    # Pass delivery_fee to template
    return render_template(
        'buyer/checkout.html',
        # ... existing params ...
        delivery_fee=delivery_fee,  # ADD THIS
        # ...
    )
```

### File: app.py (place order - need to find this endpoint)
```python
# When creating order, add:
new_order = Order(
    # ... existing fields ...
    delivery_fee=delivery_fee,  # ADD THIS
    # ...
)
```

### File: templates/buyer/checkout.html
```html
<!-- ADD THIS in order summary section -->
<div class="summary-row">
    <span>Delivery Fee ({{ address.province }}):</span>
    <span>₱{{ "%.2f"|format(delivery_fee) }}</span>
</div>
```

### File: templates/rider/available_orders.html
```html
<!-- ADD THIS in order card -->
<div class="earnings-badge">
    <i class="fas fa-money-bill-wave"></i>
    Your Earnings: ₱{{ "%.2f"|format(order.delivery_fee) }}
</div>
```

---

## 12. TESTING CHECKLIST

### Buyer Checkout
- [ ] Select address with different provinces
- [ ] Verify delivery fee changes based on province
- [ ] Check grand total includes correct delivery fee
- [ ] Verify order saves delivery_fee to database

### Rider Available Orders
- [ ] Check if delivery_fee is visible
- [ ] Verify amount matches province calculation
- [ ] Test on both web and mobile
- [ ] Confirm earnings display correctly

### Database
- [ ] Query orders table for delivery_fee values
- [ ] Verify province-based fees are saved
- [ ] Check rider wallet transactions
- [ ] Confirm commission calculations

---

## CONCLUSION

**Current Status:**
- ✅ Database schema ready (delivery_fee column exists)
- ✅ Province ranking system implemented
- ✅ Mobile API includes delivery_fee
- ✅ Rider earnings logic uses delivery_fee
- ❌ **Web checkout HINDI nag-calculate ng delivery_fee**
- ❌ **Rider web view HINDI nag-display ng delivery_fee**

**Impact:**
- Buyers see wrong shipping cost (₱50 fixed instead of province-based)
- Riders don't see their earnings before accepting
- Orders created with incorrect delivery_fee
- Commission calculations may be wrong

**Next Steps:**
1. Fix checkout calculation
2. Update order creation
3. Fix rider available orders display
4. Test end-to-end flow
5. Verify database values

---

Generated: 2025-01-XX
Status: Analysis Complete - Fixes Needed
