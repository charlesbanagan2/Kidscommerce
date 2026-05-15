# ============================================
# MOBILE-ONLY RIDER API - FIXED VERSION
# All rider functionality accessible only via mobile API
# ============================================

from flask import jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func
from werkzeug.utils import secure_filename
from flask_socketio import emit, join_room
import os

# ============================================
# HELPER FUNCTIONS
# ============================================

def push_notification(user_id, message, type=None, order_id=None, actor_user_id=None):
    """Push notification stub - implement with FCM later"""
    try:
        app.logger.info(f"Push notification to user {user_id}: {message}")
    except Exception as e:
        app.logger.error(f"Push notification error: {str(e)}")

# ============================================
# RIDER REGISTRATION API
# ============================================

@app.route('/api/v1/rider/register', methods=['POST'])
def api_rider_register():
    """Register new rider via mobile app"""
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        vehicle_type = request.form.get('vehicle_type', '').strip()
        vehicle_model = request.form.get('vehicle_model', '').strip()
        plate_number = request.form.get('plate_number', '').strip()
        
        if not all([email, password, first_name, last_name, phone, vehicle_type, plate_number]):
            return jsonify({
                'success': False,
                'error': 'All required fields must be filled'
            }), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 400
        
        # Handle file uploads
        valid_id_front = None
        valid_id_back = None
        drivers_license = None
        
        if 'valid_id_front' in request.files:
            file = request.files['valid_id_front']
            if file and file.filename:
                filename = secure_filename(f"rider_id_front_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                valid_id_front = filename
        
        if 'valid_id_back' in request.files:
            file = request.files['valid_id_back']
            if file and file.filename:
                filename = secure_filename(f"rider_id_back_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                valid_id_back = filename
        
        if 'drivers_license' in request.files:
            file = request.files['drivers_license']
            if file and file.filename:
                filename = secure_filename(f"rider_license_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                drivers_license = filename
        
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            role='rider',
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.flush()
        
        rider_details = RiderDetails(
            user_id=user.id,
            vehicle_type=vehicle_type,
            vehicle_model=vehicle_model,
            plate_number=plate_number,
            valid_id_front=valid_id_front,
            valid_id_back=valid_id_back,
            drivers_license=drivers_license,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(rider_details)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration submitted successfully. Please wait for admin approval.',
            'user_id': user.id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in rider registration: {str(e)}\")\n        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }), 500

# ============================================
# RIDER AVAILABLE ORDERS API (FCFS)
# ============================================

@app.route('/api/v1/rider/available-orders', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_available_orders():
    """Get all orders ready for pickup (FCFS)"""
    try:
        # Check if rider is approved
        user = db.session.get(User, request.current_user_id)
        if user.status != 'approved':
            return jsonify({
                'success': False,
                'error': 'Your account is not approved yet'
            }), 403
        
        orders = Order.query.filter(
            Order.status == 'ready_for_pickup',
            Order.rider_id == None
        ).order_by(Order.updated_at.desc()).all()
        
        result = []
        for order in orders:
            items = []
            seller_info = None
            
            for item in order.items:
                items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.price_at_time)
                })
                
                if not seller_info:
                    seller = item.product.seller
                    seller_app = SellerApplication.query.filter_by(
                        user_id=seller.id,
                        status='approved'
                    ).first()
                    
                    seller_info = {
                        'name': f"{seller.first_name} {seller.last_name}",
                        'phone': seller.phone or '',
                        'address': seller_app.business_address if seller_app else (seller.address or ''),
                        'profile_picture': seller.profile_picture
                    }
            
            rider_earnings = float(order.total_amount) * 0.15
            
            result.append({
                'id': order.id,
                'buyer_name': order.recipient_name or f"{order.buyer.first_name} {order.buyer.last_name}",
                'buyer_phone': order.recipient_phone or order.buyer.phone or '',
                'buyer_profile_picture': order.buyer.profile_picture,
                'delivery_address': order.shipping_address or '',
                'total_amount': float(order.total_amount),
                'rider_earnings': rider_earnings,
                'payment_method': order.payment_method or 'COD',
                'items': items,
                'seller_info': seller_info,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'orders': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching available orders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch available orders'
        }), 500

# ============================================
# RIDER ACCEPT ORDER API (FCFS with Locking)
# ============================================

@app.route('/api/v1/rider/accept-order', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_accept_order():
    """Accept order with FCFS transaction logic (thread-safe)"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Order ID is required'
            }), 400
        
        rider_id = request.current_user_id
        
        # Check if rider is approved
        rider = db.session.get(User, rider_id)
        if rider.status != 'approved':
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
        
        rider_earnings = float(order.total_amount) * 0.15
        
        order.status = 'in_transit'
        order.rider_id = rider_id
        order.picked_up_at = datetime.utcnow()
        order.picked_up_by = rider_id
        order.rider_earnings = rider_earnings
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify buyer
        try:
            socketio.emit('order_accepted_by_rider', {
                'order_id': order.id,
                'rider_name': f"{rider.first_name} {rider.last_name}",
                'rider_phone': rider.phone or '',
                'rider_profile_picture': rider.profile_picture,
                'status': 'in_transit'
            }, room=f'user_{order.buyer_id}')
            
            push_notification(
                order.buyer_id,
                f'Your order #{order.id} has been picked up by a rider!',
                type='order',
                order_id=order.id,
                actor_user_id=rider_id
            )
        except Exception as e:
            app.logger.error(f"Error sending notifications: {str(e)}")
        
        # Broadcast to all riders
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
                'buyer_name': order.recipient_name or f"{order.buyer.first_name} {order.buyer.last_name}",
                'delivery_address': order.shipping_address,
                'total_amount': float(order.total_amount),
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

# ============================================
# RIDER MY DELIVERIES API
# ============================================

@app.route('/api/v1/rider/my-deliveries', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_my_deliveries():
    """Get rider's current and past deliveries"""
    try:
        rider_id = request.current_user_id
        status_filter = request.args.get('status', None)
        
        query = Order.query.filter(Order.rider_id == rider_id)
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        orders = query.order_by(Order.updated_at.desc()).all()
        
        result = []
        for order in orders:
            items = []
            for item in order.items:
                items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.price_at_time)
                })
            
            result.append({
                'id': order.id,
                'buyer_name': order.recipient_name or f"{order.buyer.first_name} {order.buyer.last_name}",
                'buyer_phone': order.recipient_phone or order.buyer.phone or '',
                'buyer_profile_picture': order.buyer.profile_picture,
                'delivery_address': order.shipping_address or '',
                'total_amount': float(order.total_amount),
                'status': order.status,
                'payment_method': order.payment_method or 'COD',
                'items': items,
                'rider_earnings': float(order.rider_earnings) if order.rider_earnings else 0.0,
                'picked_up_at': order.picked_up_at.isoformat() if order.picked_up_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
                'created_at': order.created_at.isoformat() if order.created_at else None
            })
        
        return jsonify({
            'success': True,
            'orders': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching deliveries: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch deliveries'
        }), 500

# ============================================
# RIDER COMPLETE DELIVERY API
# ============================================

@app.route('/api/v1/rider/complete-delivery', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_complete_delivery():
    """Mark delivery as completed"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Order ID is required'
            }), 400
        
        rider_id = request.current_user_id
        
        order = Order.query.filter(
            Order.id == order_id,
            Order.rider_id == rider_id
        ).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found or not assigned to you'
            }), 404
        
        if order.status != 'in_transit':
            return jsonify({
                'success': False,
                'error': 'Order is not in transit'
            }), 400
        
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        order.delivered_by = rider_id
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify buyer
        try:
            socketio.emit('order_delivered', {
                'order_id': order.id,
                'status': 'delivered',
                'delivered_at': order.delivered_at.isoformat()
            }, room=f'user_{order.buyer_id}')
            
            push_notification(
                order.buyer_id,
                f'Your order #{order.id} has been delivered!',
                type='order',
                order_id=order.id
            )
        except Exception as e:
            app.logger.error(f"Error sending notifications: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Delivery completed successfully',
            'order': {
                'id': order.id,
                'status': order.status,
                'delivered_at': order.delivered_at.isoformat(),
                'rider_earnings': float(order.rider_earnings) if order.rider_earnings else 0.0
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error completing delivery: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to complete delivery'
        }), 500

# ============================================
# RIDER EARNINGS API
# ============================================

@app.route('/api/v1/rider/earnings', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_earnings():
    """Get rider earnings statistics"""
    try:
        rider_id = request.current_user_id
        
        total_earnings = db.session.query(
            func.sum(Order.rider_earnings)
        ).filter(
            Order.rider_id == rider_id,
            Order.status.in_(['delivered', 'completed'])
        ).scalar() or 0.0
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_earnings = db.session.query(
            func.sum(Order.rider_earnings)
        ).filter(
            Order.rider_id == rider_id,
            Order.status.in_(['delivered', 'completed']),
            Order.delivered_at >= today_start
        ).scalar() or 0.0
        
        week_start = today_start - timedelta(days=today_start.weekday())
        week_earnings = db.session.query(
            func.sum(Order.rider_earnings)
        ).filter(
            Order.rider_id == rider_id,
            Order.status.in_(['delivered', 'completed']),
            Order.delivered_at >= week_start
        ).scalar() or 0.0
        
        month_start = today_start.replace(day=1)
        month_earnings = db.session.query(
            func.sum(Order.rider_earnings)
        ).filter(
            Order.rider_id == rider_id,
            Order.status.in_(['delivered', 'completed']),
            Order.delivered_at >= month_start
        ).scalar() or 0.0
        
        total_deliveries = Order.query.filter(
            Order.rider_id == rider_id,
            Order.status.in_(['delivered', 'completed'])
        ).count()
        
        active_deliveries = Order.query.filter(
            Order.rider_id == rider_id,
            Order.status == 'in_transit'
        ).count()
        
        return jsonify({
            'success': True,
            'total': float(total_earnings),
            'today': float(today_earnings),
            'week': float(week_earnings),
            'month': float(month_earnings),
            'total_deliveries': total_deliveries,
            'active_deliveries': active_deliveries
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching earnings: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch earnings'
        }), 500

# ============================================
# RIDER PROFILE API
# ============================================

@app.route('/api/v1/rider/profile', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_get_profile():
    """Get rider profile"""
    try:
        rider_id = request.current_user_id
        user = db.session.get(User, rider_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        rider_details = RiderDetails.query.filter_by(user_id=rider_id).first()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'address': user.address,
                'profile_picture': user.profile_picture,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'rider_details': {
                'vehicle_type': rider_details.vehicle_type if rider_details else None,
                'vehicle_model': rider_details.vehicle_model if rider_details else None,
                'plate_number': rider_details.plate_number if rider_details else None,
                'status': rider_details.status if rider_details else None
            } if rider_details else None
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch profile'
        }), 500

@app.route('/api/v1/rider/profile', methods=['PUT'])
@token_required
@role_required('rider')
def api_rider_update_profile():
    """Update rider profile"""
    try:
        rider_id = request.current_user_id
        data = request.get_json()
        
        user = db.session.get(User, rider_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500

# ============================================
# SOCKET.IO EVENTS FOR RIDERS
# ============================================

@socketio.on('join_riders_room')
def handle_join_riders_room():
    """Rider joins the riders room for real-time notifications"""
    try:
        if not hasattr(request, 'current_user_id'):
            return
        
        user = db.session.get(User, request.current_user_id)
        if user and user.role == 'rider' and user.status == 'approved':
            join_room('riders')
            emit('joined_riders_room', {'message': 'Successfully joined riders room'})
    except Exception as e:
        app.logger.error(f"Error joining riders room: {str(e)}")

def broadcast_new_order_available(order_id):
    """Broadcast to all riders when order becomes available"""
    try:
        order = db.session.get(Order, order_id)
        if not order or order.status != 'ready_for_pickup':
            return
        
        items = []
        seller_info = None
        
        for item in order.items:
            items.append({
                'product_name': item.product.name,
                'quantity': item.quantity
            })
            
            if not seller_info:
                seller = item.product.seller
                seller_app = SellerApplication.query.filter_by(
                    user_id=seller.id,
                    status='approved'
                ).first()
                
                seller_info = {
                    'name': f"{seller.first_name} {seller.last_name}",
                    'phone': seller.phone or '',
                    'address': seller_app.business_address if seller_app else (seller.address or '')
                }
        
        rider_earnings = float(order.total_amount) * 0.15
        
        socketio.emit('new_order_available', {
            'id': order.id,
            'buyer_name': order.recipient_name or f"{order.buyer.first_name} {order.buyer.last_name}",
            'delivery_address': order.shipping_address or '',
            'total_amount': float(order.total_amount),
            'rider_earnings': rider_earnings,
            'items': items,
            'seller_info': seller_info,
            'created_at': order.created_at.isoformat() if order.created_at else None
        }, room='riders')
        
    except Exception as e:
        app.logger.error(f"Error broadcasting new order: {str(e)}")

def notify_riders_order_ready(order_id):
    """Called when seller marks order as ready_for_pickup"""
    try:
        order = db.session.get(Order, order_id)
        if order and order.status == 'ready_for_pickup':
            broadcast_new_order_available(order_id)
    except Exception as e:
        app.logger.error(f"Error notifying riders: {str(e)}")

# ============================================
# DISABLE RIDER WEB ROUTES
# ============================================

@app.route('/rider/<path:path>')
def rider_web_disabled(path):
    """All rider web routes are disabled - use mobile app"""
    return jsonify({
        'error': 'Rider web interface is disabled',
        'message': 'Please use the mobile app to access rider features'
    }), 410

@app.route('/rider')
def rider_web_root_disabled():
    """Rider root route disabled"""
    return jsonify({
        'error': 'Rider web interface is disabled',
        'message': 'Please use the mobile app to access rider features'
    }), 410
