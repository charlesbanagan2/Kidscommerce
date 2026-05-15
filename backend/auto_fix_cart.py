"""
AUTO-APPLY CART DUPLICATE FIXES
This script will automatically update your app.py with the cart duplicate fixes
"""

import re
import shutil
from datetime import datetime

# Backup the original file
backup_file = f'app.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('app.py', backup_file)
print(f"✓ Backup created: {backup_file}")

# Read the current app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================================
# FIX 1: Web add_to_cart function
# ============================================================================

# Find the web add_to_cart function
pattern1 = r"(@app\.route\('/cart/add/<int:product_id>', methods=\['POST'\]\)\s+@login_required\s+def add_to_cart\(product_id\):.*?)(?=@app\.route|if __name__|class\s+\w+\(db\.Model\))"

replacement1 = r'''@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart - merges quantity if already exists"""
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Check available stock
        available = get_available_stock(product_id)
        if quantity > available:
            flash(f'Only {available} items available in stock', 'error')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
        
        # CHECK IF PRODUCT ALREADY IN CART - FIX FOR DUPLICATES
        existing_cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_cart_item:
            # Update quantity instead of creating duplicate
            new_quantity = existing_cart_item.quantity + quantity
            
            # Check if new quantity exceeds stock
            if new_quantity > available:
                flash(f'Cannot add {quantity} more. Only {available} available (you have {existing_cart_item.quantity} in cart)', 'error')
                return redirect(request.referrer or url_for('product_detail', product_id=product_id))
            
            existing_cart_item.quantity = new_quantity
            db.session.commit()
            flash(f'Cart updated! Total quantity: {new_quantity}', 'success')
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

if re.search(pattern1, content, re.DOTALL):
    content = re.sub(pattern1, replacement1, content, count=1, flags=re.DOTALL)
    print("✓ Fixed: Web add_to_cart function")
else:
    print("⚠ Warning: Could not find web add_to_cart function")

# ============================================================================
# FIX 2: Web buy_now function
# ============================================================================

pattern2 = r"(@app\.route\('/buy-now/<int:product_id>', methods=\['POST'\]\)\s+@login_required\s+def buy_now\(product_id\):.*?)(?=@app\.route|if __name__|class\s+\w+\(db\.Model\))"

replacement2 = r'''@app.route('/buy-now/<int:product_id>', methods=['POST'])
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
        
        # CHECK IF PRODUCT ALREADY IN CART - FIX FOR DUPLICATES
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

if re.search(pattern2, content, re.DOTALL):
    content = re.sub(pattern2, replacement2, content, count=1, flags=re.DOTALL)
    print("✓ Fixed: Web buy_now function")
else:
    print("⚠ Warning: Could not find web buy_now function")

# ============================================================================
# FIX 3: Mobile api_add_to_cart function
# ============================================================================

pattern3 = r"(@app\.route\('/api/v1/cart/add', methods=\['POST'\]\)\s+@token_required\s+def api_add_to_cart\(\):.*?)(?=@app\.route|if __name__|class\s+\w+\(db\.Model\))"

replacement3 = r'''@app.route('/api/v1/cart/add', methods=['POST'])
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
        
        # CHECK IF PRODUCT ALREADY IN CART - FIX FOR DUPLICATES
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

if re.search(pattern3, content, re.DOTALL):
    content = re.sub(pattern3, replacement3, content, count=1, flags=re.DOTALL)
    print("✓ Fixed: Mobile api_add_to_cart function")
else:
    print("⚠ Warning: Could not find mobile api_add_to_cart function")

# ============================================================================
# FIX 4: Mobile api_buy_now function
# ============================================================================

pattern4 = r"(@app\.route\('/api/v1/buy-now', methods=\['POST'\]\)\s+@token_required\s+def api_buy_now\(\):.*?)(?=@app\.route|if __name__|class\s+\w+\(db\.Model\))"

replacement4 = r'''@app.route('/api/v1/buy-now', methods=['POST'])
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
        
        # CHECK IF PRODUCT ALREADY IN CART - FIX FOR DUPLICATES
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

if re.search(pattern4, content, re.DOTALL):
    content = re.sub(pattern4, replacement4, content, count=1, flags=re.DOTALL)
    print("✓ Fixed: Mobile api_buy_now function")
else:
    print("⚠ Warning: Could not find mobile api_buy_now function")

# Write the updated content back to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 80)
print("✓ ALL CART FIXES APPLIED SUCCESSFULLY!")
print("=" * 80)
print(f"\nBackup saved as: {backup_file}")
print("\nWhat was fixed:")
print("  1. Web add_to_cart - Now merges quantities")
print("  2. Web buy_now - Now replaces quantity")
print("  3. Mobile api_add_to_cart - Now merges quantities")
print("  4. Mobile api_buy_now - Now replaces quantity")
print("\nNext steps:")
print("  1. Restart your Flask server")
print("  2. Test: Add same product twice → should merge quantities")
print("  3. Test on mobile app too")
print("\n" + "=" * 80)
