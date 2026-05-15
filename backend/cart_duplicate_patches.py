"""
Cart Duplicate Fix - Apply this patch to app.py

This script shows the code changes needed to fix cart duplicate items.
Copy and paste these functions into your app.py, replacing the existing ones.
"""

# ============================================================================
# WEB ROUTES - Replace these in app.py
# ============================================================================

WEB_ADD_TO_CART = '''
@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart - merges quantity if already exists"""
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Check if product already in cart
        existing_cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_cart_item:
            # Update quantity instead of creating duplicate
            existing_cart_item.quantity += quantity
            db.session.commit()
            flash(f'Cart updated! Total quantity: {existing_cart_item.quantity}', 'success')
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
        
        # Emit real-time cart update
        try:
            socketio.emit('cart_updated', {
                'user_id': session['user_id'],
                'cart_count': get_cart_count()
            }, room=f"user_{session['user_id']}")
        except:
            pass
        
        return redirect(request.referrer or url_for('cart'))
    except Exception as e:
        app.logger.error(f'Error adding to cart: {e}')
        flash('Error adding product to cart', 'error')
        return redirect(request.referrer or url_for('index'))
'''

WEB_BUY_NOW = '''
@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    """Buy now - sets quantity for immediate checkout"""
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
        
        # Check available stock
        available = get_available_stock(product_id)
        if quantity > available:
            flash(f'Only {available} items available in stock', 'error')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Check if product already in cart
        existing_cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_cart_item:
            # Replace quantity for buy now (not add)
            existing_cart_item.quantity = quantity
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
    except Exception as e:
        app.logger.error(f'Error in buy now: {e}')
        flash('Error processing buy now', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
'''

# ============================================================================
# MOBILE API ROUTES - Replace these in app.py
# ============================================================================

MOBILE_ADD_TO_CART = '''
@app.route('/api/v1/cart/add', methods=['POST'])
@token_required
def api_add_to_cart():
    """Mobile API: Add to cart - merges quantity if exists (Supabase version)"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if not product_id or quantity <= 0:
            return jsonify({'success': False, 'error': 'Invalid product or quantity'}), 400
        
        # Check if product exists and is active
        product = get_data_by_id('product', product_id)
        if not product or product.get('status') != 'active':
            return jsonify({'success': False, 'error': 'Product not available'}), 404
        
        # Check available stock
        available = get_available_stock(product_id)
        if quantity > available:
            return jsonify({
                'success': False, 
                'error': f'Only {available} items available in stock'
            }), 400
        
        # Check if product already in cart
        existing_items = get_data('cart', filters={
            'user_id': request.current_user_id,
            'product_id': product_id
        })
        
        if existing_items and len(existing_items) > 0:
            # Update existing cart item quantity
            existing_item = existing_items[0]
            new_quantity = existing_item.get('quantity', 0) + quantity
            
            # Check if new quantity exceeds stock
            if new_quantity > available:
                return jsonify({
                    'success': False,
                    'error': f'Cannot add {quantity} more. Only {available} available (you have {existing_item.get("quantity", 0)} in cart)'
                }), 400
            
            updated_item = update_data_by_id('cart', existing_item['id'], {'quantity': new_quantity})
            
            return jsonify({
                'success': True,
                'message': f'Cart updated! Total quantity: {new_quantity}',
                'cart_item': {
                    'id': updated_item.get('id'),
                    'product_id': product_id,
                    'quantity': new_quantity,
                    'product': product
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
            
            if not new_item:
                return jsonify({'success': False, 'error': 'Failed to add to cart'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Product added to cart',
                'cart_item': {
                    'id': new_item.get('id'),
                    'product_id': product_id,
                    'quantity': quantity,
                    'product': product
                }
            })
    except Exception as e:
        app.logger.error(f'api_add_to_cart error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
'''

MOBILE_BUY_NOW = '''
@app.route('/api/v1/buy-now', methods=['POST'])
@token_required
def api_buy_now():
    """Mobile API: Buy now - sets quantity for immediate checkout (Supabase version)"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if not product_id or quantity <= 0:
            return jsonify({'success': False, 'error': 'Invalid product or quantity'}), 400
        
        # Check if product exists
        product = get_data_by_id('product', product_id)
        if not product or product.get('status') != 'active':
            return jsonify({'success': False, 'error': 'Product not available'}), 404
        
        # Check available stock
        available = get_available_stock(product_id)
        if quantity > available:
            return jsonify({
                'success': False,
                'error': f'Only {available} items available in stock'
            }), 400
        
        # Check if product already in cart
        existing_items = get_data('cart', filters={
            'user_id': request.current_user_id,
            'product_id': product_id
        })
        
        if existing_items and len(existing_items) > 0:
            # Replace quantity for buy now (not add)
            existing_item = existing_items[0]
            updated_item = update_data_by_id('cart', existing_item['id'], {'quantity': quantity})
            
            return jsonify({
                'success': True,
                'message': 'Proceeding to checkout',
                'cart_item': {
                    'id': updated_item.get('id'),
                    'product_id': product_id,
                    'quantity': quantity,
                    'product': product
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
            
            if not new_item:
                return jsonify({'success': False, 'error': 'Failed to process buy now'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Proceeding to checkout',
                'cart_item': {
                    'id': new_item.get('id'),
                    'product_id': product_id,
                    'quantity': quantity,
                    'product': product
                }
            })
    except Exception as e:
        app.logger.error(f'api_buy_now error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
'''

print("=" * 80)
print("CART DUPLICATE FIX - CODE PATCHES")
print("=" * 80)
print("\n1. WEB ADD TO CART ROUTE:")
print(WEB_ADD_TO_CART)
print("\n2. WEB BUY NOW ROUTE:")
print(WEB_BUY_NOW)
print("\n3. MOBILE ADD TO CART API:")
print(MOBILE_ADD_TO_CART)
print("\n4. MOBILE BUY NOW API:")
print(MOBILE_BUY_NOW)
print("\n" + "=" * 80)
print("INSTRUCTIONS:")
print("=" * 80)
print("1. Find each route in app.py")
print("2. Replace with the code above")
print("3. Run cleanup_cart_duplicates.sql in Supabase")
print("4. Test: Add same product twice → should merge quantities")
print("=" * 80)
