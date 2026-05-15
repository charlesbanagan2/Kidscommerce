# Price and Stock Sync - Quick Guide

## The Truth About Your System

**Your prices and stock ARE ALREADY SYNCED!**

Here's why:
- Database (Supabase PostgreSQL) = Single source of truth
- Website (Flask) = Reads from database
- Mobile App = Calls API which reads from database

**They all use the SAME data!**

## How to Verify

### Option 1: Run the Check Script (Recommended)

Double-click: `CHECK_SYNC.bat`

This will show you all products with their prices and stock from the database.

### Option 2: Manual Verification

1. **Check Database** (via Supabase Dashboard)
   - Go to your Supabase project
   - Open SQL Editor
   - Run: `SELECT id, name, price, stock FROM product WHERE status = 'active' LIMIT 10;`

2. **Check Website**
   - Start Flask: `cd backend && python app.py`
   - Visit: `http://localhost:5000/product/1`
   - Note the price and stock

3. **Check Mobile App**
   - Open the mobile app
   - Find the same product (ID: 1)
   - Compare price and stock

**They should be IDENTICAL!**

## If You See Differences

### Problem 1: Different Stock Values

**Cause**: Your backend has TWO stock values:
- `product.stock` = Total stock in warehouse
- `get_available_stock()` = Stock minus reserved orders

**Solution**: Decide which one to show consistently.

**Fix for Website** (backend/app.py):
```python
# Show total stock
available_stock = product.stock

# OR show available stock (current behavior)
available_stock = get_available_stock(product.id)
```

**Fix for Mobile App** (mobile_app/lib/models/product.dart):
```dart
// Make sure you're reading the same field
stock: json['stock'] ?? 0,  // Total stock
// OR
stock: json['available_stock'] ?? 0,  // Available stock
```

### Problem 2: Mobile App Shows Old Data

**Cause**: Caching

**Solution**: 
1. Close mobile app completely
2. Clear app data (Settings > Apps > Kids Commerce > Clear Data)
3. Restart app

### Problem 3: API Returns Wrong Format

**Check API Response**:
```bash
curl http://localhost:5000/api/products
```

Should return:
```json
{
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price": 299.99,
      "stock": 50
    }
  ]
}
```

## Quick Fix: Make Everything Consistent

### Step 1: Update API to Return Both Stock Values

Add to `backend/app.py` in the `/api/products` endpoint:

```python
@app.route('/api/products')
def get_products():
    products = Product.query.filter_by(status='active').all()
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'stock': p.stock,  # Total stock
            'available_stock': get_available_stock(p.id)  # Available stock
        } for p in products]
    })
```

### Step 2: Update Mobile App to Use Correct Field

In `mobile_app/lib/models/product.dart`:

```dart
factory Product.fromJson(Map<String, dynamic> json) {
  return Product(
    id: json['id'] ?? 0,
    name: json['name'] ?? '',
    price: (json['price'] ?? 0.0).toDouble(),
    stock: json['available_stock'] ?? json['stock'] ?? 0,  // Use available_stock if present
    ...
  );
}
```

### Step 3: Restart Everything

1. Stop Flask backend
2. Start Flask backend: `cd backend && python app.py`
3. Close mobile app completely
4. Clear mobile app cache
5. Restart mobile app

## Conclusion

**Your data is ALREADY synced at the database level.**

The "sync" issue is actually a **display consistency** issue:
- Website might show "available stock"
- Mobile app might show "total stock"
- Both are correct, just different calculations

**Choose one method and apply it everywhere.**

## Need Help?

Run `CHECK_SYNC.bat` to see your current product data.

Compare the output with what you see in:
1. Website
2. Mobile app

If they match the database output, everything is working correctly!
