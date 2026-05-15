# N+1 Query Problem - The Most Common Performance Issue

## What is N+1?

When you load a list of items and then access their relationships, SQLAlchemy makes **1 query for the list + N queries for each relationship**.

Example:
```python
# 1 query to get products
products = Product.query.filter_by(status='active').all()  

# Then N queries (one per product!)
for product in products:
    print(product.seller.first_name)  # Query 1
    print(product.category.name)       # Query 2
```

If you have 24 products, this makes **1 + (24 × 2) = 49 queries!** 😱

---

## The Fix: Eager Loading with joinedload()

Load relationships in the initial query:

```python
from sqlalchemy.orm import joinedload

# ONE query that loads products + sellers + categories
products = Product.query.options(
    joinedload(Product.seller),
    joinedload(Product.category)
).filter_by(status='active').all()

# Now these don't trigger extra queries
for product in products:
    print(product.seller.first_name)  # Already loaded!
    print(product.category.name)       # Already loaded!
```

**Result: 49 queries → 1 query = 49x faster!** ⚡

---

## Apply These Fixes to Your Routes

### 1. Homepage (index route) - Line ~3682

**BEFORE (Slow):**
```python
@app.route('/')
def index():
    products = Product.query.filter_by(status='active').order_by(Product.created_at.desc()).all()
    # ... rest of code
```

**AFTER (Fast):**
```python
from sqlalchemy.orm import joinedload

@app.route('/')
def index():
    products = Product.query.options(
        joinedload(Product.seller),
        joinedload(Product.category)
    ).filter_by(status='active').order_by(Product.created_at.desc()).all()
    # ... rest of code
```

---

### 2. Shop/Product Listing

**BEFORE:**
```python
products = Product.query.filter_by(status='active').all()
```

**AFTER:**
```python
products = Product.query.options(
    joinedload(Product.seller),
    joinedload(Product.category),
    joinedload(Product.subcategory)
).filter_by(status='active').all()
```

---

### 3. Order History

**BEFORE:**
```python
orders = Order.query.filter_by(buyer_id=user_id).all()
for order in orders:
    for item in order.items:  # N+1 here!
        print(item.product.name)  # Another N+1!
```

**AFTER:**
```python
from sqlalchemy.orm import joinedload

orders = Order.query.options(
    joinedload(Order.items).joinedload(OrderItem.product),
    joinedload(Order.buyer)
).filter_by(buyer_id=user_id).all()
```

---

### 4. Seller Dashboard

**BEFORE:**
```python
products = Product.query.filter_by(seller_id=seller_id).all()
```

**AFTER:**
```python
products = Product.query.options(
    joinedload(Product.category),
    joinedload(Product.subcategory)
).filter_by(seller_id=seller_id).all()
```

---

### 5. Admin Dashboard

**BEFORE:**
```python
recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
```

**AFTER:**
```python
recent_orders = Order.query.options(
    joinedload(Order.buyer),
    joinedload(Order.items).joinedload(OrderItem.product)
).order_by(Order.created_at.desc()).limit(10).all()
```

---

## Quick Test

Add this to any route to see the difference:

```python
from flask import Flask
from flask_sqlalchemy import get_debug_queries

app.config['SQLALCHEMY_RECORD_QUERIES'] = True

@app.after_request
def after_request(response):
    queries = get_debug_queries()
    print(f"Total queries: {len(queries)}")
    for query in queries:
        if query.duration > 0.01:  # Slow queries
            print(f"SLOW: {query.duration:.3f}s - {query.statement[:100]}")
    return response
```

---

## Expected Results

| Route | Before | After | Queries |
|-------|--------|-------|---------|
| Homepage | 3-5s | 0.3s | 49 → 1 |
| Shop | 2-4s | 0.2s | 73 → 1 |
| Orders | 2-3s | 0.3s | 31 → 1 |

---

## Other Common N+1 Locations

Search your code for these patterns:

```python
# Pattern 1: Loop accessing relationships
for item in items:
    item.relationship.field  # ⚠️ N+1!

# Pattern 2: Template accessing relationships
{% for product in products %}
    {{ product.seller.name }}  {# ⚠️ N+1! #}
{% endfor %}

# Pattern 3: List comprehension
[order.buyer.email for order in orders]  # ⚠️ N+1!
```

**Fix all of these with joinedload()!**

---

## Run This Now

1. Run advanced diagnostic:
   ```bash
   python diagnose_advanced.py
   ```

2. If it shows "N+1 PROBLEM DETECTED", apply the fixes above

3. Test the difference - should be 10-50x faster!
