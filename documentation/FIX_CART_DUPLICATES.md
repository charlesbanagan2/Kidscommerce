# FIX: Cart Duplicate Items Issue

## Problem
When adding the same product to cart multiple times, it creates separate cart items instead of updating the quantity.

Example:
- Add Product A (2 qty) → Cart has 1 item with qty 2
- Add Product A (3 qty) again → Cart has 2 items (qty 2 and qty 3) ❌
- Should be: Cart has 1 item with qty 5 ✅

## Solution

### Backend Fix (app.py)

Find these routes and update them:

#### 1. Web Add to Cart Route
```python
@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product already in cart
    existing_cart_item = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if existing_cart_item:
        # Update quantity instead of creating new item
        existing_cart_item.quantity += quantity
        db.session.commit()
        flash(f'Updated cart quantity to {existing_cart_item.quantity}', 'success')
    else:
        # Create new cart item
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
        flash('Product added to cart!', 'success')
    
    return redirect(url_for('cart'))
```

#### 2. Mobile API Add to Cart Route
```python
@app.route('/api/v1/cart/add', methods=['POST'])
@token_required
def api_add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    # Check if product already in cart (Supabase version)
    existing_items = get_data('cart', filters={
        'user_id': request.current_user_id,
        'product_id': product_id
    })
    
    if existing_items and len(existing_items) > 0:
        # Update existing cart item quantity
        existing_item = existing_items[0]
        new_quantity = existing_item.get('quantity', 0) + quantity
        update_data_by_id('cart', existing_item['id'], {'quantity': new_quantity})
        
        return jsonify({
            'success': True,
            'message': f'Updated cart quantity to {new_quantity}',
            'cart_item': {
                'id': existing_item['id'],
                'quantity': new_quantity
            }
        })
    else:
        # Create new cart item
        cart_data = {
            'user_id': request.current_user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        new_item = insert_data('cart', cart_data)
        
        return jsonify({
            'success': True,
            'message': 'Product added to cart',
            'cart_item': new_item
        })
```

#### 3. Buy Now Route
```python
@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product already in cart
    existing_cart_item = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if existing_cart_item:
        # Update quantity
        existing_cart_item.quantity = quantity  # Replace with new quantity for buy now
        db.session.commit()
    else:
        # Create new cart item
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
    
    return redirect(url_for('checkout'))
```

### Mobile App Fix (Flutter)

#### File: `mobile_app/lib/services/cart_service.dart`

```dart
Future<bool> addToCart(int productId, int quantity) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/cart/add'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'product_id': productId,
        'quantity': quantity,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Backend now handles merging automatically
      return data['success'] == true;
    }
    return false;
  } catch (e) {
    print('Error adding to cart: $e');
    return false;
  }
}
```

## Testing Steps

1. **Clear existing duplicate cart items:**
   ```sql
   -- Run in Supabase SQL Editor
   DELETE FROM cart 
   WHERE id NOT IN (
     SELECT MIN(id) 
     FROM cart 
     GROUP BY user_id, product_id
   );
   ```

2. **Test Web:**
   - Add Product A (qty 2) to cart
   - Add Product A (qty 3) to cart again
   - Check cart page → Should show 1 item with qty 5

3. **Test Mobile:**
   - Add Product B (qty 1) to cart
   - Add Product B (qty 2) to cart again
   - Check cart screen → Should show 1 item with qty 3

4. **Test Buy Now:**
   - Click "Buy Now" with qty 4
   - Go to checkout → Should show qty 4 (not duplicated)

## Database Constraint (Optional - Prevent Future Duplicates)

Add a unique constraint to prevent duplicate cart entries:

```sql
-- Run in Supabase SQL Editor
ALTER TABLE cart 
ADD CONSTRAINT cart_user_product_unique 
UNIQUE (user_id, product_id);
```

This ensures the database itself prevents duplicate entries.

## Summary

✅ Backend checks for existing cart items before adding
✅ Updates quantity instead of creating duplicates
✅ Mobile app uses same logic via API
✅ Buy Now replaces quantity for immediate checkout
✅ Database constraint prevents future duplicates
