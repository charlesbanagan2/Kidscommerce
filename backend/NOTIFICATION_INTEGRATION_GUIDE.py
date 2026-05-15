# Integration Guide - Add to app.py

"""
STEP 1: Import notification service and routes
Add these imports at the top of app.py:
"""

from notification_service import NotificationService, Notification
from notification_routes import notification_bp

"""
STEP 2: Register notification blueprint
Add after other blueprint registrations:
"""

app.register_blueprint(notification_bp)

"""
STEP 3: Integrate notifications into order status changes
Replace existing order status update code with these:
"""

# Example 1: When buyer places order (in checkout route)
@app.route('/checkout', methods=['POST'])
def checkout():
    # ... existing checkout code ...
    
    # After order is created successfully:
    NotificationService.notify_new_order(order)
    
    # ... rest of code ...

# Example 2: When seller processes order
@app.route('/seller/order/<int:order_id>/process', methods=['POST'])
def seller_process_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'processing'
    db.session.commit()
    
    # Send notification
    NotificationService.notify_order_processing(order)
    
    return jsonify({'success': True})

# Example 3: When seller marks ready for pickup
@app.route('/seller/order/<int:order_id>/ready-for-pickup', methods=['POST'])
def seller_ready_for_pickup(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'ready_for_pickup'
    db.session.commit()
    
    # Notify all riders
    NotificationService.notify_ready_for_pickup(order)
    
    return jsonify({'success': True})

# Example 4: When rider accepts order
@app.route('/api/rider/orders/<int:order_id>/accept', methods=['POST'])
def rider_accept_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.rider_id = g.current_user['id']
    order.status = 'to_ship'
    db.session.commit()
    
    # Notify buyer and seller
    NotificationService.notify_rider_assigned(order)
    
    return jsonify({'success': True})

# Example 5: When rider marks out for delivery
@app.route('/api/rider/orders/<int:order_id>/out-for-delivery', methods=['POST'])
def rider_out_for_delivery(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'out_for_delivery'
    db.session.commit()
    
    # Notify buyer
    NotificationService.notify_out_for_delivery(order)
    
    return jsonify({'success': True})

# Example 6: When rider marks delivered
@app.route('/api/rider/orders/<int:order_id>/delivered', methods=['POST'])
def rider_mark_delivered(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'delivered'
    db.session.commit()
    
    # Notify buyer and seller
    NotificationService.notify_delivered(order)
    
    return jsonify({'success': True})

# Example 7: When buyer confirms receipt
@app.route('/buyer/order/<int:order_id>/confirm-receipt', methods=['POST'])
def buyer_confirm_receipt(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'completed'
    
    # Update rider earnings
    if order.rider_id:
        rider = User.query.get(order.rider_id)
        rider.wallet_balance = (rider.wallet_balance or 0) + order.shipping_fee
    
    db.session.commit()
    
    # Notify rider with earnings
    NotificationService.notify_order_completed(order)
    
    return jsonify({'success': True})

"""
STEP 4: Add SocketIO event handlers for real-time notifications
Add these SocketIO handlers:
"""

@socketio.on('join_notification_room')
def handle_join_notification_room(data):
    """User joins their notification room"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_id and user_role:
        room = f"{user_role}_{user_id}"
        join_room(room)
        emit('joined_notification_room', {'room': room})

@socketio.on('disconnect')
def handle_disconnect():
    """User disconnects"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_id and user_role:
        room = f"{user_role}_{user_id}"
        leave_room(room)

"""
STEP 5: Create database migration
Run these commands:
"""

# flask db migrate -m "Add notifications table"
# flask db upgrade

"""
STEP 6: Add notification badge to templates
Add this to base.html or navigation:
"""

# <span class="notification-badge" id="notificationBadge">0</span>

# <script>
# // Fetch unread count on page load
# fetch('/api/notifications/unread-count')
#     .then(r => r.json())
#     .then(data => {
#         document.getElementById('notificationBadge').textContent = data.unread_count;
#     });
# 
# // Listen for real-time notifications
# socket.on('new_notification', function(data) {
#     // Update badge count
#     const badge = document.getElementById('notificationBadge');
#     badge.textContent = parseInt(badge.textContent) + 1;
#     
#     // Show toast notification
#     showToast(data.title, data.message);
# });
# </script>

"""
STEP 7: Test the system
1. Place an order as buyer
2. Check seller receives notification
3. Process order as seller
4. Check buyer receives notification
5. Continue through all status changes
"""
