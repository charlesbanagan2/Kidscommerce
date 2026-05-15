# RIDER ACCEPT/DECLINE ENDPOINTS
# Insert these after the /api/v1/rider/available-orders endpoint in app.py

@app.route('/api/v1/rider/orders/<int:order_id>/accept', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_accept_order(order_id):
    """
    Rider accepts an order (FCFS with row-level locking)
    """
    try:
        rider_id = request.current_user_id
        
        # Check if rider is approved
        rider = db.session.get(User, rider_id)
        if not rider or rider.status != 'approved':
            return jsonify({
                'success': False,
                'error': 'Your account is not approved'
            }), 403
        
        # CRITICAL: Row-level locking for FCFS
        order = db.session.query(Order).filter(
            Order.id == order_id
        ).with_for_update().first()
        
        if not order:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # FCFS Check
        if order.status != 'ready_for_pickup':
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409
        
        if order.rider_id is not None:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409
        
        # Calculate rider earnings (15% of order total)
        rider_earnings = float(order.total_amount) * 0.15
        
        # Update order
        order.status = 'in_transit'
        order.rider_id = rider_id
        order.picked_up_at = datetime.utcnow()
        order.picked_up_by = rider_id
        order.rider_earnings = rider_earnings
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify buyer via Socket.IO
        try:
            socketio.emit('order_accepted_by_rider', {
                'order_id': order.id,
                'rider_name': f"{rider.first_name} {rider.last_name}",
                'rider_phone': rider.phone or '',
                'status': 'in_transit'
            }, room=f'user_{order.buyer_id}')
        except Exception as e:
            app.logger.error(f"Error sending socket notification: {str(e)}")
        
        # Broadcast to all riders that order is taken
        try:
            socketio.emit('order_claimed', {
                'order_id': order.id,
                'rider_id': rider_id
            }, room='riders')
        except Exception as e:
            app.logger.error(f"Error broadcasting order_claimed: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Order accepted successfully',
            'order': {
                'id': order.id,
                'status': order.status,
                'rider_earnings': rider_earnings,
                'picked_up_at': order.picked_up_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error accepting order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to accept order'
        }), 500


@app.route('/api/v1/rider/orders/<int:order_id>/decline', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_decline_order(order_id):
    """
    Rider declines an order (just removes it from their view)
    """
    try:
        rider_id = request.current_user_id
        
        # Check if order exists and is available
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        if order.status != 'ready_for_pickup':
            return jsonify({
                'success': False,
                'error': 'Order is no longer available'
            }), 400
        
        # Just return success - order stays available for other riders
        return jsonify({
            'success': True,
            'message': 'Order declined'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error declining order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to decline order'
        }), 500
