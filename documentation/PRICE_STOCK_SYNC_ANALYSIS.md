# Price and Stock Synchronization - Analysis and Solution

## Current Architecture

Your system uses a **single database** (Supabase PostgreSQL) as the source of truth:

```
┌─────────────────────────────────────┐
│   Supabase PostgreSQL Database      │
│   (Single Source of Truth)          │
│   - product.price                   │
│   - product.stock                   │
└─────────────────────────────────────┘
           ↓                ↓
    ┌──────────┐      ┌──────────┐
    │ Website  │      │ Mobile   │
    │ (Flask)  │      │ App      │
    │          │      │ (API)    │
    └──────────┘      └──────────┘
```

## Key Finding

**Prices and stock ARE already the same** across all platforms because:

1. **Database**: Stores the actual values in `product` table
2. **Website**: Reads directly from database via SQLAlchemy ORM
3. **Mobile App**: Calls Flask API which reads from the same database

## Data Flow

### Website (Flask Backend)
```python
# app.py - Direct database access
product = Product.query.get(product_id)
price = product.price      # Direct from database
stock = product.stock      # Direct from database
```

### Mobile App API
```python
# app.py - /api/products endpoint
@app.route('/api/products')
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,    # Same database field
        'stock': p.stock,    # Same database field
        ...
    }])
```

### Mobile App Model
```dart
// product.dart
class Product {
  final double price;
  final int stock;
  
  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      price: (json['price'] ?? 0.0).toDouble(),
      stock: json['stock'] ?? 0,
      ...
    );
  }
}
```

## Why They Appear Different

If you're seeing different values, it's likely due to:

### 1. **Available Stock vs Total Stock**

The backend has a `get_available_stock()` function that calculates:
```python
available_stock = product.stock - reserved_orders - completed_orders
```

**Solution**: Ensure both website and mobile app use the same stock calculation method.

### 2. **Caching**

Mobile app might cache product data.

**Solution**: Clear app cache or force refresh.

### 3. **Different Products**

You might be comparing different products.

**Solution**: Verify you're looking at the same product ID.

## Verification Steps

### Step 1: Check Database
```sql
SELECT id, name, price, stock 
FROM product 
WHERE id = 1;
```

### Step 2: Check Website
Visit: `http://localhost:5000/product/1`

### Step 3: Check Mobile API
```bash
curl http://localhost:5000/api/products
```

### Step 4: Compare Values
All three should show **identical** price and stock.

## Solution Implementation

Since your data is already synced at the database level, you need to ensure:

### 1. **Consistent Stock Calculation**

Both website and mobile app should use the same logic:

**Option A**: Show total stock (product.stock)
**Option B**: Show available stock (product.stock - reserved)

Choose one and apply it consistently.

### 2. **API Response Format**

Ensure the API returns data in the expected format:

```json
{
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "price": 299.99,
      "stock": 50,
      "available_stock": 45
    }
  ]
}
```

### 3. **Mobile App Display**

Update mobile app to use the correct field:

```dart
// If using available stock
Text('Stock: ${product.availableStock ?? product.stock}')

// If using total stock
Text('Stock: ${product.stock}')
```

## Recommended Actions

1. **Decide on stock display logic**: Total or Available?
2. **Update API to include both values** if needed
3. **Update mobile app** to use consistent field
4. **Clear mobile app cache** after changes
5. **Test with specific product** to verify sync

## Conclusion

Your prices and stock **ARE synced** because they come from the same database. Any perceived differences are due to:
- Different calculation methods (total vs available stock)
- Caching
- Display logic differences

The fix is to ensure **consistent display logic** across platforms, not to sync the data (which is already synced).
