"""
Stock Management Helper Functions
Add these functions to app.py for real-time stock management
"""

# ============================================================================
# STOCK RESERVATION SYSTEM - Add to app.py
# ============================================================================

# Add this model after other models in app.py
class OrderStockReservation(db.Model):
    """Track stock reservations for orders"""
    __tablename__ = 'order_stock_reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, released, completed
    
    order = db.relationship('Order', backref='stock_reservations')
    product = db.relationship('Product', backref='stock_reservations')


# Helper Functions - Add these to app.py

def get_available_stock_new(product_id):
    """
    Get available stock (total stock - reserved stock)
    This is the NEW version that accounts for reservations
    """
    product = db.session.get(Product, product_id)
    if not product:
        return 0
    
    reserved = product.reserved_stock or 0
    available = product.stock - reserved
    return max(0, available)


def reserve_stock(order_id, product_id, quantity):
    """
    Reserve stock when order is placed
    Returns True if successful, False if insufficient stock
    """
    product = db.session.get(Product, product_id)
    if not product:
        return False
    
    # Check if enough stock available
    available = product.stock - (product.reserved_stock or 0)
    if available < quantity:
        return False
    
    # Increase reserved stock
    product.reserved_stock = (product.reserved_stock or 0) + quantity
    
    # Create reservation record
    reservation = OrderStockReservation(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        status='active'
    )
    db.session.add(reservation)
    
    try:
        db.session.commit()
        
        # Broadcast stock update
        broadcast_stock_update(product_id)
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to reserve stock: {e}")
        return False


def release_stock(order_id):
    """
    Release reserved stock when order is cancelled
    Returns list of product IDs that were updated
    """
    reservations = OrderStockReservation.query.filter_by(
        order_id=order_id,
        status='active'
    ).all()
    
    updated_products = []
    
    for reservation in reservations:
        product = db.session.get(Product, reservation.product_id)
        if product:
            # Decrease reserved stock
            product.reserved_stock = max(0, (product.reserved_stock or 0) - reservation.quantity)
            
            # Mark reservation as released
            reservation.status = 'released'
            reservation.released_at = datetime.utcnow()
            
            updated_products.append(reservation.product_id)
    
    try:
        db.session.commit()
        
        # Broadcast stock updates
        for product_id in updated_products:
            broadcast_stock_update(product_id)
        
        return updated_products
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to release stock: {e}")
        return []


def complete_stock_reservation(order_id):
    """
    Complete stock reservation when order is delivered/completed
    Deducts from actual stock and clears reservation
    """
    reservations = OrderStockReservation.query.filter_by(
        order_id=order_id,
        status='active'
    ).all()
    
    updated_products = []
    
    for reservation in reservations:
        product = db.session.get(Product, reservation.product_id)
        if product:
            # Deduct from actual stock
            product.stock = max(0, product.stock - reservation.quantity)
            
            # Decrease reserved stock
            product.reserved_stock = max(0, (product.reserved_stock or 0) - reservation.quantity)
            
            # Mark reservation as completed
            reservation.status = 'completed'
            
            updated_products.append(reservation.product_id)
    
    try:
        db.session.commit()
        
        # Broadcast stock updates
        for product_id in updated_products:
            broadcast_stock_update(product_id)
        
        return updated_products
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to complete stock reservation: {e}")
        return []


def broadcast_stock_update(product_id):
    """
    Broadcast stock update to all connected clients (web and mobile)
    """
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return
        
        reserved = product.reserved_stock or 0
        available = product.stock - reserved
        
        # Emit to web clients via SocketIO
        socketio.emit('product_stock_update', {
            'product_id': product_id,
            'stock': product.stock,
            'reserved_stock': reserved,
            'available_stock': max(0, available),
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
        
        app.logger.info(f"Stock update broadcast: Product {product_id}, Available: {available}")
    except Exception as e:
        app.logger.error(f"Failed to broadcast stock update: {e}")


def broadcast_price_update(product_id):
    """
    Broadcast price update to all connected clients
    """
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return
        
        # Emit to web clients via SocketIO
        socketio.emit('product_price_update', {
            'product_id': product_id,
            'price': float(product.price),
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
        
        app.logger.info(f"Price update broadcast: Product {product_id}, Price: {product.price}")
    except Exception as e:
        app.logger.error(f"Failed to broadcast price update: {e}")


# ============================================================================
# UPDATE EXISTING ROUTES - Replace these sections in app.py
# ============================================================================

"""
CHECKOUT ROUTE - Replace the existing checkout route with this:
"""
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        # Get cart items
        cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
        
        if not cart_items:
            flash('Your cart is empty', 'warning')
            return redirect(url_for('cart'))
        
        # STEP 1: Validate stock availability BEFORE creating order
        for item in cart_items:
            product = db.session.get(Product, item.product_id)
            available = product.stock - (product.reserved_stock or 0)
            
            if available < item.quantity:
                flash(f'{product.name} only has {available} items available. Please update your cart.', 'error')
                return redirect(url_for('cart'))
        
        # STEP 2: Create order
        shipping_address = request.form.get('shipping_address')
        payment_method = request.form.get('payment_method')
        
        # Calculate total
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order(
            buyer_id=session['user_id'],
            total_amount=subtotal,
            payment_method=payment_method,
            shipping_address=shipping_address,
            status='pending',
            payment_status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # STEP 3: Reserve stock IMMEDIATELY and create order items
        for item in cart_items:
            # Reserve stock
            if not reserve_stock(order.id, item.product_id, item.quantity):
                db.session.rollback()
                flash(f'Failed to reserve stock for {item.product.name}', 'error')
                return redirect(url_for('cart'))
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_time=item.product.price
            )
            db.session.add(order_item)
        
        # STEP 4: Clear cart
        Cart.query.filter_by(user_id=session['user_id']).delete()
        
        db.session.commit()
        
        flash('Order placed successfully! Stock has been reserved.', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    # GET request - show checkout form
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal)


"""
CANCEL ORDER ROUTE - Add this new route or update existing:
"""
@app.route('/seller/cancel-order/<int:order_id>', methods=['POST'])
@seller_required
def seller_cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Verify seller owns this order
    order_items = order.items
    if not any(item.product.seller_id == session['user_id'] for item in order_items):
        flash('Unauthorized', 'error')
        return redirect(url_for('seller_orders'))
    
    # Release reserved stock
    released_products = release_stock(order_id)
    
    # Update order status
    order.status = 'cancelled'
    db.session.commit()
    
    flash(f'Order cancelled. Stock has been released for {len(released_products)} product(s).', 'success')
    return redirect(url_for('seller_orders'))


"""
COMPLETE ORDER ROUTE - Update existing or add:
"""
@app.route('/seller/complete-order/<int:order_id>', methods=['POST'])
@seller_required
def seller_complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Complete stock reservation (deduct actual stock)
    completed_products = complete_stock_reservation(order_id)
    
    # Update order status
    order.status = 'completed'
    db.session.commit()
    
    flash(f'Order completed. Stock deducted for {len(completed_products)} product(s).', 'success')
    return redirect(url_for('seller_orders'))


"""
API PRODUCTS ENDPOINT - Replace existing:
"""
@app.route('/api/products')
def api_products():
    products = Product.query.filter_by(status='active').all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'stock': p.stock,
        'reserved_stock': p.reserved_stock or 0,
        'available_stock': p.stock - (p.reserved_stock or 0),
        'image_filename': p.image_filename,
        'category_id': p.category_id,
        'description': p.description
    } for p in products])


"""
UPDATE PRODUCT PRICE - Add this route:
"""
@app.route('/seller/update-product-price/<int:product_id>', methods=['POST'])
@seller_required
def update_product_price(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Verify ownership
    if product.seller_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        new_price = float(request.form.get('price') or request.json.get('price'))
        
        if new_price <= 0:
            return jsonify({'success': False, 'message': 'Price must be greater than 0'}), 400
        
        product.price = new_price
        db.session.commit()
        
        # Broadcast price update
        broadcast_price_update(product_id)
        
        return jsonify({
            'success': True,
            'message': 'Price updated successfully',
            'new_price': new_price
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
