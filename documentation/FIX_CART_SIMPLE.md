# FIX CART DUPLICATES - SIMPLE STEPS

## Problem
Same product appears multiple times in cart instead of merging quantities.

## Quick Fix (3 Steps)

### Step 1: Clean Database (2 minutes)
Run this in **Supabase SQL Editor**:

```sql
-- Merge duplicate cart items
CREATE TEMP TABLE cart_merged AS
SELECT 
    MIN(id) as id,
    user_id,
    product_id,
    SUM(quantity) as quantity,
    MIN(created_at) as created_at
FROM cart
GROUP BY user_id, product_id;

DELETE FROM cart;

INSERT INTO cart (id, user_id, product_id, quantity, created_at)
SELECT id, user_id, product_id, quantity, created_at
FROM cart_merged;

SELECT setval('cart_id_seq', COALESCE((SELECT MAX(id) FROM cart), 0) + 1, false);

-- Prevent future duplicates
ALTER TABLE cart 
ADD CONSTRAINT cart_user_product_unique 
UNIQUE (user_id, product_id);
```

### Step 2: Update Backend Code

Open `backend/app.py` and find these 4 routes. I'll tell you what to change:

#### A. Find: `def add_to_cart(product_id):`
Look for this line inside the function:
```python
cart_item = Cart(...)
db.session.add(cart_item)
```

**ADD BEFORE IT:**
```python
# Check if already in cart
existing = Cart.query.filter_by(
    user_id=session['user_id'],
    product_id=product_id
).first()

if existing:
    existing.quantity += quantity
    db.session.commit()
    flash(f'Cart updated! Total: {existing.quantity}', 'success')
    return redirect(request.referrer or url_for('cart'))
```

#### B. Find: `def buy_now(product_id):`
Same thing - add the check before creating cart item:
```python
existing = Cart.query.filter_by(
    user_id=session['user_id'],
    product_id=product_id
).first()

if existing:
    existing.quantity = quantity  # Replace, not add
    db.session.commit()
else:
    # ... create new cart item
```

#### C. Find: `def api_add_to_cart():` (Mobile API)
Add after getting product_id and quantity:
```python
# Check if already in cart
existing_items = get_data('cart', filters={
    'user_id': request.current_user_id,
    'product_id': product_id
})

if existing_items and len(existing_items) > 0:
    existing = existing_items[0]
    new_qty = existing.get('quantity', 0) + quantity
    update_data_by_id('cart', existing['id'], {'quantity': new_qty})
    return jsonify({
        'success': True,
        'message': f'Cart updated! Total: {new_qty}'
    })
```

#### D. Find: `def api_buy_now():` (Mobile API)
Same pattern - check and update instead of insert.

### Step 3: Test

**Web:**
1. Add Product A (qty 2)
2. Add Product A (qty 3) again
3. Cart should show: 1 item with qty 5 ✅

**Mobile:**
1. Add Product B (qty 1)
2. Add Product B (qty 2) again
3. Cart should show: 1 item with qty 3 ✅

## Files Created for You

1. **cleanup_cart_duplicates.sql** - Run this in Supabase first
2. **cart_duplicate_patches.py** - Full code examples
3. **FIX_CART_DUPLICATES.md** - Detailed guide

## Need Help?

If you're not sure where to add the code:
1. Open `cart_duplicate_patches.py`
2. It shows the COMPLETE functions with fixes
3. Copy the entire function and replace in app.py

## Summary

✅ Database cleaned and protected
✅ Backend checks for existing cart items
✅ Quantities merge instead of duplicate
✅ Works on web and mobile
