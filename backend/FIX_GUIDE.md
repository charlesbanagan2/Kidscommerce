# PRODUCT VISIBILITY FIX GUIDE

## Problem
Products have status='active' but the code filters for status='approved', so buyers can't see them.

## Solution
Update all product queries to include both 'approved' and 'active' statuses.

## Quick Fix Steps

### Step 1: Run the automated fix script
```bash
python fix_all_status_filters.py
```

This will automatically update all product status filters in app.py.

### Step 2: Restart Flask server
Stop your current Flask server (Ctrl+C) and restart it:
```bash
python app.py
```

### Step 3: Clear browser cache
Press Ctrl+Shift+R in your browser to hard refresh.

## Manual Fix (if automated script fails)

Search for these patterns in app.py and replace them:

### Pattern 1: Homepage (index route)
**Find:**
```python
products = Product.query.filter_by(status='approved')
```

**Replace with:**
```python
products = Product.query.filter(Product.status.in_(['approved', 'active']))
```

### Pattern 2: Shop page
**Find:**
```python
query = Product.query.filter_by(status='approved')
```

**Replace with:**
```python
query = Product.query.filter(Product.status.in_(['approved', 'active']))
```

### Pattern 3: API endpoints
**Find all occurrences of:**
```python
.filter_by(status='approved')
```

**Replace with:**
```python
.filter(Product.status.in_(['approved', 'active']))
```

## Verification

After fixing, verify by:
1. Opening homepage (/) - should see 24 products
2. Opening shop page (/shop) - should see all products
3. Check product count in browser console

## Alternative: Change product status in database

If you prefer to keep the code as-is, change all products from 'active' to 'approved':

```python
from app import app, db, Product

with app.app_context():
    products = Product.query.filter_by(status='active').all()
    for p in products:
        p.status = 'approved'
    db.session.commit()
    print(f"Updated {len(products)} products to 'approved' status")
```

Save this as `change_status_to_approved.py` and run it.
