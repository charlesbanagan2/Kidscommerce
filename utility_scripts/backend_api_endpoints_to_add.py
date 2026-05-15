"""
Backend API endpoints for buyer cart and checkout operations
These endpoints provide the mobile app with cart management and order creation functionality
"""

# Add these endpoints to backend/app.py

# ============= BUYER CART ENDPOINTS =============

@app.route('/api/v1/buyer/cart', methods=['GET'])
@token_required
def buyer_get_cart():
    """Get current buyer's cart items"""
    try:
        cart_data = _serialize_cart(request.current_user_id)
        return jsonify({
            'success': True,
            'items': cart_data['items'],
            'item_count': cart_data['item_count'],
            'total_price': cart_data['total_price'],
        })
    except Exception as e:
        app.logger.error(f'buyer_get_cart error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/cart/add', methods=['POST'])
@token_required
def buyer_add_to_cart():
    """Add item to buyer's cart"""
    try:
        data = request.get_json(silent=True) or {}
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'success': False, 'error': 'product_id required'}), 400
        
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except:
            return jsonify({'success': False, 'error': 'Invalid product_id or quantity'}), 400
        
        if quantity < 1:
            return jsonify({'success': False, 'error': 'Quantity must be >= 1'}), 400
        
        product = Product.query.get(product_id)
        if not product or product.status != 'active':
            return jsonify({'success': False, 'error': 'Product not found or inactive'}), 404
        
        if product.stock < quantity:
            return jsonify({'success': False, 'error': f'Only {product.stock} in stock'}), 400
        
        # Find existing cart item
        cart_item = Cart.query.filter_by(
            user_id=request.current_user_id,
            product_id=product_id
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            db.session.commit()
        else:
            # Create new cart item
            cart_item = Cart(
                user_id=request.current_user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'item': {
                'id': cart_item.id,
                'product_id': product_id,
                'product_name': product.name,
                'product_image': _safe_upload_url(product.image_filename),
                'quantity': cart_item.quantity,
                'price': float(product.price),
                'stock': product.stock,
                'subtotal': float(cart_item.quantity * product.price),
            },
            'message': 'Item added to cart'
        })
    except Exception as e:
        app.logger.error(f'buyer_add_to_cart error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['PUT'])
@token_required
def buyer_update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        cart_item = Cart.query.filter_by(
            id=item_id,
            user_id=request.current_user_id
        ).first()
        
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        data = request.get_json(silent=True) or {}
        quantity = data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
        except:
            return jsonify({'success': False, 'error': 'Invalid quantity'}), 400
        
        if quantity < 1:
            return jsonify({'success': False, 'error': 'Quantity must be >= 1'}), 400
        
        product = cart_item.product
        if not product or product.status != 'active':
            return jsonify({'success': False, 'error': 'Product not available'}), 404
        
        if product.stock < quantity:
            return jsonify({'success': False, 'error': f'Only {product.stock} in stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': {
                'id': cart_item.id,
                'product_id': product.id,
                'quantity': cart_item.quantity,
                'subtotal': float(cart_item.quantity * product.price),
            }
        })
    except Exception as e:
        app.logger.error(f'buyer_update_cart_item error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['DELETE'])
@token_required
def buyer_remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        cart_item = Cart.query.filter_by(
            id=item_id,
            user_id=request.current_user_id
        ).first()
        
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    except Exception as e:
        app.logger.error(f'buyer_remove_from_cart error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/cart/clear', methods=['POST'])
@token_required
def buyer_clear_cart():
    """Clear all items from cart"""
    try:
        Cart.query.filter_by(user_id=request.current_user_id).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cart cleared'})
    except Exception as e:
        app.logger.error(f'buyer_clear_cart error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# ============= BUYER CHECKOUT/ORDER ENDPOINTS =============

@app.route('/api/v1/buyer/checkout', methods=['POST'])
@token_required
def buyer_checkout():
    """Create order from cart"""
    try:
        data = request.get_json(silent=True) or {}
        
        recipient_name = str(data.get('recipient_name', '')).strip()
        recipient_phone = str(data.get('recipient_phone', '')).strip()
        shipping_address = str(data.get('shipping_address', '')).strip()
        payment_method = str(data.get('payment_method', 'cod')).strip()
        notes = str(data.get('notes', '')).strip()
        selected_items = data.get('selected_items', [])  # List of cart item IDs
        
        if not recipient_name or not recipient_phone or not shipping_address:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get cart items
        if selected_items:
            cart_items = Cart.query.filter(
                Cart.user_id == request.current_user_id,
                Cart.id.in_(selected_items)
            ).all()
        else:
            cart_items = Cart.query.filter_by(user_id=request.current_user_id).all()
        
        if not cart_items:
            return jsonify({'success': False, 'error': 'Cart is empty'}), 400
        
        # Verify all items are available
        order_items_data = []
        total_amount = 0
        
        for cart_item in cart_items:
            product = cart_item.product
            if not product or product.status != 'active':
                return jsonify({'success': False, 'error': f'Product {product.name if product else "unknown"} is not available'}), 400
            
            if product.stock < cart_item.quantity:
                return jsonify({'success': False, 'error': f'{product.name}: Only {product.stock} in stock'}), 400
            
            subtotal = float(product.price) * cart_item.quantity
            total_amount += subtotal
            order_items_data.append({
                'product': product,
                'quantity': cart_item.quantity,
                'price_at_time': float(product.price),
            })
        
        # Create order
        order = Order(
            buyer_id=request.current_user_id,
            total_amount=total_amount,
            status='to_pay',
            payment_method=payment_method,
            payment_status='pending',
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            shipping_address=shipping_address,
            notes=notes,
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item_data in order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price_at_time = item_data['price_at_time']
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_time=price_at_time,
            )
            db.session.add(order_item)
            
            # Deduct stock
            product.stock -= quantity
        
        # Clear cart
        Cart.query.filter_by(user_id=request.current_user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'payment_method': order.payment_method,
                'created_at': order.created_at.isoformat() if order.created_at else None,
            },
            'message': 'Order created successfully'
        })
    except Exception as e:
        app.logger.error(f'buyer_checkout error: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/orders', methods=['GET'])
@token_required
def buyer_get_orders():
    """Get all orders for current buyer"""
    try:
        status = request.args.get('status')
        
        query = Order.query.filter_by(buyer_id=request.current_user_id)
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'orders': [_serialize_order_api(order) for order in orders],
        })
    except Exception as e:
        app.logger.error(f'buyer_get_orders error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/v1/buyer/orders/<int:order_id>', methods=['GET'])
@token_required
def buyer_get_order(order_id):
    """Get specific order details"""
    try:
        order = Order.query.filter_by(
            id=order_id,
            buyer_id=request.current_user_id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': _serialize_order_api(order),
        })
    except Exception as e:
        app.logger.error(f'buyer_get_order error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400
