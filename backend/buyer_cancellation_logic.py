"""
BUYER CANCELLATION LOGIC WITH STOCK MANAGEMENT
Add these routes and functions to app.py
"""

# ============================================================================
# BUYER CANCELLATION ROUTES - Add to app.py
# ============================================================================

@app.route('/buyer/cancel-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def cancel_order(order_id):
    """
    Buyer cancels order with automatic stock release logic:
    - If order is 'pending' or 'to_pay': Direct cancellation, stock released immediately
    - If order is 'processing' or later: Request cancellation, seller must approve
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify buyer owns this order
    if order.buyer_id != session['user_id']:
        flash('Unauthorized', 'error')
        return redirect(url_for('my_orders'))
    
    # Check if order can be cancelled
    if order.status in ['completed', 'delivered', 'cancelled']:
        flash('This order cannot be cancelled', 'error')
        return redirect(url_for('my_orders'))
    
    if request.method == 'GET':
        return render_template('buyer/cancel_order.html', order=order)
    
    # POST - Process cancellation
    cancel_reasons = request.form.getlist('cancel_reasons')
    cancel_other = request.form.get('cancel_other', '').strip()
    
    # Combine reasons
    reasons = ', '.join(cancel_reasons)
    if cancel_other:
        reasons += f' | Other: {cancel_other}'
    
    # LOGIC: Direct cancel vs Request cancel
    if order.status in ['pending', 'to_pay']:
        # DIRECT CANCELLATION - Seller hasn't processed yet
        order.status = 'cancelled'
        order.return_reason = f'Buyer cancelled: {reasons}'
        order.updated_at = datetime.utcnow()
        
        # Release reserved stock IMMEDIATELY
        released_products = release_stock(order_id)
        
        db.session.commit()
        
        # Notify seller
        for item in order.items:
            try:
                push_notification(
                    item.product.seller_id,
                    f'Order #{order_id} was cancelled by buyer before processing',
                    type='order_cancelled',
                    link=url_for('seller_orders'),
                    order_id=order_id
                )
            except:
                pass
        
        flash(f'Order cancelled successfully. Stock has been released for {len(released_products)} product(s).', 'success')
        return redirect(url_for('my_orders'))
    
    else:
        # REQUEST CANCELLATION - Seller has already processed
        # Create cancellation request (don't cancel yet)
        order.status = 'cancellation_requested'
        order.return_reason = f'Buyer requests cancellation: {reasons}'
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify seller to approve/reject
        for item in order.items:
            try:
                push_notification(
                    item.product.seller_id,
                    f'Buyer requests to cancel Order #{order_id}. Please review.',
                    type='cancellation_request',
                    link=url_for('seller_order_detail', order_id=order_id),
                    order_id=order_id
                )
            except:
                pass
        
        flash('Cancellation request sent to seller. You will be notified once reviewed.', 'info')
        return redirect(url_for('my_orders'))


@app.route('/seller/approve-cancellation/<int:order_id>', methods=['POST'])
@seller_required
def seller_approve_cancellation(order_id):
    """
    Seller approves buyer's cancellation request
    Stock is released when approved
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify seller owns products in this order
    if not any(item.product.seller_id == session['user_id'] for item in order.items):
        flash('Unauthorized', 'error')
        return redirect(url_for('seller_orders'))
    
    if order.status != 'cancellation_requested':
        flash('This order does not have a pending cancellation request', 'error')
        return redirect(url_for('seller_orders'))
    
    # Approve cancellation
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    # Release reserved stock
    released_products = release_stock(order_id)
    
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(
            order.buyer_id,
            f'Your cancellation request for Order #{order_id} has been approved. Stock released.',
            type='cancellation_approved',
            link=url_for('order_detail', order_id=order_id),
            order_id=order_id
        )
    except:
        pass
    
    flash(f'Cancellation approved. Stock released for {len(released_products)} product(s).', 'success')
    return redirect(url_for('seller_orders'))


@app.route('/seller/reject-cancellation/<int:order_id>', methods=['POST'])
@seller_required
def seller_reject_cancellation(order_id):
    """
    Seller rejects buyer's cancellation request
    Order continues with original status
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify seller owns products in this order
    if not any(item.product.seller_id == session['user_id'] for item in order.items):
        flash('Unauthorized', 'error')
        return redirect(url_for('seller_orders'))
    
    if order.status != 'cancellation_requested':
        flash('This order does not have a pending cancellation request', 'error')
        return redirect(url_for('seller_orders'))
    
    rejection_reason = request.form.get('rejection_reason', '').strip()
    
    # Reject cancellation - restore to processing
    order.status = 'processing'
    order.return_reason = f'Cancellation rejected by seller: {rejection_reason}'
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(
            order.buyer_id,
            f'Your cancellation request for Order #{order_id} was rejected by seller.',
            type='cancellation_rejected',
            link=url_for('order_detail', order_id=order_id),
            order_id=order_id
        )
    except:
        pass
    
    flash('Cancellation request rejected. Order continues.', 'info')
    return redirect(url_for('seller_orders'))


# ============================================================================
# MOBILE API ENDPOINTS - Add to app.py
# ============================================================================

@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@token_required
def api_cancel_order(order_id):
    """
    Mobile API: Buyer cancels order
    Same logic as web version
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify buyer owns this order
    if order.buyer_id != request.current_user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Check if order can be cancelled
    if order.status in ['completed', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'message': 'This order cannot be cancelled'}), 400
    
    data = request.get_json() or {}
    reasons = data.get('reasons', [])
    other_reason = data.get('other_reason', '').strip()
    
    # Combine reasons
    reason_text = ', '.join(reasons)
    if other_reason:
        reason_text += f' | Other: {other_reason}'
    
    # LOGIC: Direct cancel vs Request cancel
    if order.status in ['pending', 'to_pay']:
        # DIRECT CANCELLATION
        order.status = 'cancelled'
        order.return_reason = f'Buyer cancelled: {reason_text}'
        order.updated_at = datetime.utcnow()
        
        # Release reserved stock
        released_products = release_stock(order_id)
        
        db.session.commit()
        
        # Notify seller
        for item in order.items:
            try:
                push_notification(
                    item.product.seller_id,
                    f'Order #{order_id} was cancelled by buyer before processing',
                    type='order_cancelled',
                    order_id=order_id
                )
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': f'Order cancelled. Stock released for {len(released_products)} product(s).',
            'order_status': 'cancelled',
            'stock_released': True
        })
    
    else:
        # REQUEST CANCELLATION
        order.status = 'cancellation_requested'
        order.return_reason = f'Buyer requests cancellation: {reason_text}'
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify seller
        for item in order.items:
            try:
                push_notification(
                    item.product.seller_id,
                    f'Buyer requests to cancel Order #{order_id}',
                    type='cancellation_request',
                    order_id=order_id
                )
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': 'Cancellation request sent to seller',
            'order_status': 'cancellation_requested',
            'requires_seller_approval': True
        })


@app.route('/api/orders/<int:order_id>/approve-cancellation', methods=['POST'])
@token_required
@role_required('seller')
def api_approve_cancellation(order_id):
    """
    Mobile API: Seller approves cancellation
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify seller owns products
    if not any(item.product.seller_id == request.current_user_id for item in order.items):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if order.status != 'cancellation_requested':
        return jsonify({'success': False, 'message': 'No pending cancellation request'}), 400
    
    # Approve cancellation
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    # Release stock
    released_products = release_stock(order_id)
    
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(
            order.buyer_id,
            f'Your cancellation request for Order #{order_id} has been approved',
            type='cancellation_approved',
            order_id=order_id
        )
    except:
        pass
    
    return jsonify({
        'success': True,
        'message': f'Cancellation approved. Stock released for {len(released_products)} product(s).',
        'order_status': 'cancelled',
        'products_released': len(released_products)
    })


@app.route('/api/orders/<int:order_id>/reject-cancellation', methods=['POST'])
@token_required
@role_required('seller')
def api_reject_cancellation(order_id):
    """
    Mobile API: Seller rejects cancellation
    """
    order = Order.query.get_or_404(order_id)
    
    # Verify seller owns products
    if not any(item.product.seller_id == request.current_user_id for item in order.items):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if order.status != 'cancellation_requested':
        return jsonify({'success': False, 'message': 'No pending cancellation request'}), 400
    
    data = request.get_json() or {}
    rejection_reason = data.get('reason', '').strip()
    
    # Reject cancellation
    order.status = 'processing'
    order.return_reason = f'Cancellation rejected: {rejection_reason}'
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(
            order.buyer_id,
            f'Your cancellation request for Order #{order_id} was rejected',
            type='cancellation_rejected',
            order_id=order_id
        )
    except:
        pass
    
    return jsonify({
        'success': True,
        'message': 'Cancellation request rejected',
        'order_status': 'processing'
    })


# ============================================================================
# UPDATE ORDER STATUS CONSTANTS - Add to app.py
# ============================================================================

# Order status flow with cancellation:
ORDER_STATUS_FLOW = {
    'pending': ['to_pay', 'cancelled'],  # Buyer can cancel directly
    'to_pay': ['processing', 'cancelled'],  # Buyer can cancel directly
    'processing': ['ready_for_pickup', 'cancellation_requested'],  # Buyer must request
    'ready_for_pickup': ['in_transit', 'cancellation_requested'],
    'in_transit': ['delivered', 'cancellation_requested'],
    'delivered': ['completed'],
    'cancellation_requested': ['cancelled', 'processing'],  # Seller approves/rejects
    'cancelled': [],  # Terminal state
    'completed': []  # Terminal state
}


# ============================================================================
# HELPER FUNCTION - Update release_stock() in app.py
# ============================================================================

def release_stock(order_id):
    """
    Release reserved stock when order is cancelled
    Returns list of product IDs that were updated
    
    UPDATED VERSION: Handles both buyer and seller cancellations
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
            
            app.logger.info(f"Released {reservation.quantity} stock for product {reservation.product_id}")
    
    try:
        db.session.commit()
        
        # Broadcast stock updates to all clients
        for product_id in updated_products:
            broadcast_stock_update(product_id)
        
        return updated_products
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to release stock: {e}")
        return []
