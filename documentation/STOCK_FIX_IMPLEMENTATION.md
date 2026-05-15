# STOCK SYNCHRONIZATION - COMPLETE IMPLEMENTATION GUIDE

## Current Situation

Your system has:
- **Database**: `product.stock` = actual inventory (e.g., 100)
- **Website**: Uses `get_available_stock()` which calculates differently
- **Mobile App**: Reads from API which might use `get_available_stock()`

This causes **different stock values** to appear in different places.

## The Fix

Make everything use `product.stock` directly - the actual database value.

---

## Step 1: Update Backend API

**File**: `backend/app.py`

**Find this pattern** (search for `/api/products` or `def get_products`):

```python
@app.route('/api/products')
def get_products():
    products = Product.query.filter_by(status='active').all()
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'stock': get_available_stock(p.id),  # ← CHANGE THIS LINE
            ...
        } for p in products]
    })
```

**Change to**:

```python
@app.route('/api/products')
def get_products():
    products = Product.query.filter_by(status='active').all()
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'stock': p.stock,  # ← USE DIRECT DATABASE VALUE
            ...
        } for p in products]
    })
```

---

## Step 2: Update Website Product Detail Page

**File**: `backend/templates/product_detail.html`

**Find**:
```html
<div class="stock">
    Stock: {{ get_available_stock(product.id) }}
</div>
```

**Change to**:
```html
<div class="stock">
    Stock: {{ product.stock }}
</div>
```

**Also find**:
```html
{% if get_available_stock(product.id) > 0 %}
```

**Change to**:
```html
{% if product.stock > 0 %}
```

---

## Step 3: Update Shop/Product Listing Page

**File**: `backend/templates/shop.html`

**Find**:
```html
<div class="product-stock">
    {{ get_available_stock(product.id) }} in stock
</div>
```

**Change to**:
```html
<div class="product-stock">
    {{ product.stock }} in stock
</div>
```

---

## Step 4: Mobile App (NO CHANGES NEEDED)

The mobile app `Product` model already correctly reads the `stock` field:

```dart
// mobile_app/lib/models/product.dart
stock: json['stock'] ?? 0,  // ✓ Already correct
```

It will automatically show whatever the API returns.

---

## Step 5: Test Everything

### 1. Check Database
```sql
SELECT id, name, price, stock FROM product WHERE id = 1;
```
Note the stock value (e.g., 100)

### 2. Check Website
- Visit: `http://localhost:5000/product/1`
- Should show: Stock: 100

### 3. Check API
```bash
curl http://localhost:5000/api/products
```
Should return: `"stock": 100`

### 4. Check Mobile App
- Open the product in mobile app
- Should display: 100 in stock

**All four should show THE SAME value!**

---

## Why This Works

### Before Fix:
```
Database: product.stock = 100
↓
get_available_stock() calculates: 100 - 20 (reserved) = 80
↓
Website shows: 80
API returns: 80
Mobile app shows: 80
```

But the database still says 100! Confusing!

### After Fix:
```
Database: product.stock = 100
↓
Website shows: product.stock = 100
API returns: product.stock = 100
Mobile app shows: 100
```

Everything shows the SAME value because they all read `product.stock` directly!

---

## Quick Search Commands

To find what needs to be changed:

### In app.py:
```
Search for: @app.route('/api/products')
Or search for: get_available_stock
```

### In templates:
```
Search for: get_available_stock
Replace all with: product.stock
```

---

## Summary

**Change 3 things:**

1. **backend/app.py** - API endpoint: `'stock': p.stock`
2. **backend/templates/product_detail.html** - Template: `{{ product.stock }}`
3. **backend/templates/shop.html** - Template: `{{ product.stock }}`

**Result:** Database stock = Website stock = API stock = Mobile app stock ✓

---

## Need Help?

If you can't find the exact code, run:
```bash
cd backend
grep -n "get_available_stock" app.py
grep -n "get_available_stock" templates/*.html
```

This will show you the exact line numbers to change.
