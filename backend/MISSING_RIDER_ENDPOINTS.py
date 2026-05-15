# Missing Rider API Endpoints for Mobile App
# Add these endpoints to app.py after the existing rider routes (around line 13874)

# 1. PUT /api/orders/status - Update order status
@app.route('/api/orders/status', methods=['PUT'])
@token_required
def api_update_order_status():
    """Update order status (for riders to update delivery status)"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        if not order_id or not new_status:
            return jsonify({'error': 'order_id and status are required'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify rider is assigned to this order
        if request.current_user_role == 'rider' and order.rider_id != request.current_user_id:
            return jsonify({'error': 'Not authorized to update this order'}), 403
        
        # Update order status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Update timestamps based on status
        if new_status == 'picked_up':
            order.picked_up_at = datetime.utcnow()
            order.picked_up_by = request.current_user_id
        elif new_status == 'in_transit':
            pass  # Already picked up
        elif new_status == 'delivered':
            order.delivered_at = datetime.utcnow()
            order.delivered_by = request.current_user_id
        
        db.session.commit()
        
        # Notify buyer
        try:
            push_notification(
                order.buyer_id,
                f'Your order #{order.id} status updated to: {new_status}',
                type='order',
                order_id=order.id
            )
        except:
            pass
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'status': order.status,
                'updated_at': order.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error updating order status: {e}")
        return jsonify({'error': 'Failed to update order status'}), 500


# 2. POST /api/v1/rider/orders/<id>/accept - Accept delivery order
@app.route('/api/v1/rider/orders/<int:order_id>/accept', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_accept_order(order_id):
    """Rider accepts a delivery order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if order is available for pickup
        if order.status not in ['ready_for_pickup', 'pending']:
            return jsonify({'error': 'Order not available for pickup'}), 400
        
        # Check if already assigned to another rider
        if order.rider_id and order.rider_id != request.current_user_id:
            return jsonify({'error': 'Order already assigned to another rider'}), 400
        
        # Assign rider and update status
        order.rider_id = request.current_user_id
        order.status = 'accepted_by_rider'
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify buyer
        try:
            rider = User.query.get(request.current_user_id)
            push_notification(
                order.buyer_id,
                f'Rider {rider.first_name} has accepted your order #{order.id}',
                type='order',
                order_id=order.id,
                actor_user_id=request.current_user_id
            )
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Order accepted successfully',
            'order': {
                'id': order.id,
                'status': order.status,
                'rider_id': order.rider_id
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error accepting order: {e}")
        return jsonify({'error': 'Failed to accept order'}), 500


# 3. POST /api/v1/rider/orders/<id>/decline - Decline delivery order
@app.route('/api/v1/rider/orders/<int:order_id>/decline', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_decline_order(order_id):
    """Rider declines a delivery order"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if rider is assigned
        if order.rider_id != request.current_user_id:
            return jsonify({'error': 'Not authorized to decline this order'}), 403
        
        # Unassign rider and revert status
        order.rider_id = None
        order.status = 'ready_for_pickup'
        order.delivery_notes = f"Declined by rider: {reason}"
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify admins
        try:
            rider = User.query.get(request.current_user_id)
            notify_admins(
                f'Rider {rider.first_name} declined order #{order.id}. Reason: {reason}',
                type='order',
                link=f'/admin/orders/{order.id}'
            )
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Order declined successfully'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error declining order: {e}")
        return jsonify({'error': 'Failed to decline order'}), 500


# 4. POST /api/v1/qr-scan - QR code scan endpoint (fix path from /api/qr-scan)
@app.route('/api/v1/qr-scan', methods=['POST'])
@token_required
def api_v1_qr_scan():
    """QR code scan endpoint for mobile app (v1 path)"""
    try:
        data = request.get_json()
        qr_code = data.get('qr_code')
        scan_type = data.get('scan_type', 'delivery')
        
        if not qr_code:
            return jsonify({'error': 'qr_code is required'}), 400
        
        # Find order by QR code
        order = Order.query.filter_by(qr_code=qr_code).first()
        if not order:
            return jsonify({'error': 'Invalid QR code'}), 404
        
        # Verify rider is assigned to this order
        if request.current_user_role == 'rider' and order.rider_id != request.current_user_id:
            return jsonify({'error': 'Not authorized for this order'}), 403
        
        # Update order based on scan type
        if scan_type == 'pickup':
            order.status = 'picked_up'
            order.picked_up_at = datetime.utcnow()
            order.picked_up_by = request.current_user_id
        elif scan_type == 'delivery':
            order.status = 'delivered'
            order.delivered_at = datetime.utcnow()
            order.delivered_by = request.current_user_id
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log QR scan
        try:
            label = OrderLabel.query.filter_by(qr_code=qr_code).first()
            if label:
                scan_log = QRScanLog(
                    order_id=order.id,
                    order_label_id=label.id,
                    qr_code=qr_code,
                    scanned_by=request.current_user_id,
                    scan_type=scan_type,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')
                )
                db.session.add(scan_log)
                db.session.commit()
        except:
            pass
        
        # Notify buyer
        try:
            status_msg = 'picked up' if scan_type == 'pickup' else 'delivered'
            push_notification(
                order.buyer_id,
                f'Your order #{order.id} has been {status_msg}',
                type='order',
                order_id=order.id
            )
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'Order {scan_type} confirmed',
            'order': {
                'id': order.id,
                'status': order.status,
                'qr_code': order.qr_code,
                'tracking_number': order.tracking_number
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error processing QR scan: {e}")
        return jsonify({'error': 'Failed to process QR scan'}), 500
