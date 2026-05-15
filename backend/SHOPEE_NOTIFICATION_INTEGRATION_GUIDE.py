"""
SHOPEE-STYLE NOTIFICATION SYSTEM - COMPLETE INTEGRATION GUIDE
==============================================================

Ito ay comprehensive notification system na katulad ng Shopee.
Lahat ng order status changes, payment updates, at iba pang events
ay may corresponding notifications para sa buyer, seller, at rider.

FEATURES:
---------
✓ Real-time notifications via SocketIO
✓ Database persistence (notifications saved sa database)
✓ Mobile API endpoints (para sa Flutter app)
✓ Email notifications (optional)
✓ Notification filtering by type
✓ Mark as read/unread
✓ Notification history
✓ Push notifications support

INSTALLATION STEPS:
-------------------

1. BACKEND SETUP (app.py)
   
   Add these imports at the top of app.py:
   
   ```python
   from shopee_notification_system import (
       ensure_notification_table,
       notify_order_placed,
       notify_order_confirmed,
       notify_order_processing,
       notify_order_ready_for_pickup,
       notify_order_accepted_by_rider,
       notify_order_in_transit,
       notify_order_delivered,
       notify_order_completed,
       notify_order_cancelled,
       notify_payment_confirmed,
       notify_return_requested,
       notify_return_approved,
       notify_return_rejected,
       notify_refund_processed,
       notify_product_approved,
       notify_product_rejected,
       notify_low_stock,
       notify_out_of_stock,
       integrate_with_order_status_change
   )
   from notification_api_endpoints import register_notification_api
   ```
   
   Add after app initialization:
   
   ```python
   # Register notification API
   register_notification_api(app)
   
   # Ensure notification table has all columns
   with app.app_context():
       ensure_notification_table()
   ```

2. INTEGRATE WITH ORDER STATUS CHANGES
   
   Find all places where order.status is updated and add notification:
   
   Example 1: When buyer places order
   ```python
   @app.route('/api/checkout', methods=['POST'])
   @token_required
   def api_checkout():
       # ... existing checkout code ...
       
       # After order is created
       db.session.commit()
       
       # Send notifications
       notify_order_placed(order)
       
       return jsonify({'success': True, 'order_id': order.id})
   ```
   
   Example 2: When seller processes order
   ```python
   @app.route('/seller/orders/<int:order_id>/process', methods=['POST'])
   @seller_required
   def seller_process_order(order_id):
       order = Order.query.get_or_404(order_id)
       
       old_status = order.status
       order.status = 'processing'
       db.session.commit()
       
       # Send notification
       notify_order_processing(order)
       
       flash('Order is now being processed', 'success')
       return redirect(url_for('seller_orders'))
   ```
   
   Example 3: When rider accepts order
   ```python
   @app.route('/api/rider/orders/<int:order_id>/accept', methods=['POST'])
   @token_required
   @role_required('rider')
   def api_rider_accept_order(order_id):
       order = Order.query.get_or_404(order_id)
       
       order.status = 'accepted_by_rider'
       order.rider_id = request.current_user_id
       db.session.commit()
       
       # Send notifications
       notify_order_accepted_by_rider(order)
       
       return jsonify({'success': True})
   ```
   
   Example 4: When order is delivered
   ```python
   @app.route('/api/rider/orders/<int:order_id>/deliver', methods=['POST'])
   @token_required
   @role_required('rider')
   def api_rider_mark_delivered(order_id):
       order = Order.query.get_or_404(order_id)
       
       order.status = 'delivered'
       order.delivered_at = datetime.utcnow()
       db.session.commit()
       
       # Send notifications
       notify_order_delivered(order)
       
       return jsonify({'success': True})
   ```
   
   Example 5: When buyer confirms receipt
   ```python
   @app.route('/api/orders/<int:order_id>/confirm', methods=['POST'])
   @token_required
   def api_confirm_order(order_id):
       order = Order.query.get_or_404(order_id)
       
       order.status = 'completed'
       db.session.commit()
       
       # Release commissions
       _release_commissions(order)
       
       # Send notifications
       notify_order_completed(order)
       
       return jsonify({'success': True})
   ```

3. INTEGRATE WITH PAYMENT UPDATES
   
   ```python
   @app.route('/api/orders/<int:order_id>/payment/confirm', methods=['POST'])
   def confirm_payment(order_id):
       order = Order.query.get_or_404(order_id)
       
       order.payment_status = 'paid'
       db.session.commit()
       
       # Send notification
       notify_payment_confirmed(order)
       
       return jsonify({'success': True})
   ```

4. INTEGRATE WITH RETURN/REFUND
   
   ```python
   @app.route('/api/orders/<int:order_id>/return', methods=['POST'])
   @token_required
   def request_return(order_id):
       # ... create return request ...
       
       return_request = ReturnRequest(...)
       db.session.add(return_request)
       db.session.commit()
       
       # Send notification
       notify_return_requested(return_request)
       
       return jsonify({'success': True})
   ```

5. INTEGRATE WITH PRODUCT APPROVAL
   
   ```python
   @app.route('/admin/products/<int:product_id>/approve', methods=['POST'])
   @admin_required
   def approve_product(product_id):
       product = Product.query.get_or_404(product_id)
       
       product.status = 'approved'
       db.session.commit()
       
       # Send notification
       notify_product_approved(product)
       
       flash('Product approved', 'success')
       return redirect(url_for('admin_products'))
   ```

6. INTEGRATE WITH STOCK ALERTS
   
   ```python
   def check_stock_levels():
       \"\"\"Run this periodically (e.g., daily cron job)\"\"\"
       products = Product.query.filter(Product.stock <= 5, Product.stock > 0).all()
       
       for product in products:
           notify_low_stock(product)
       
       out_of_stock = Product.query.filter_by(stock=0).all()
       for product in out_of_stock:
           notify_out_of_stock(product)
   ```

MOBILE APP INTEGRATION (Flutter):
----------------------------------

1. CREATE NOTIFICATION SERVICE
   
   File: lib/services/notification_service.dart
   
   ```dart
   import 'package:http/http.dart' as http;
   import 'dart:convert';
   
   class NotificationService {
     final String baseUrl = 'YOUR_API_URL';
     
     Future<List<Notification>> getNotifications({
       int limit = 50,
       int offset = 0,
       bool unreadOnly = false,
       String? type,
     }) async {
       final token = await getAuthToken();
       
       var url = '$baseUrl/api/v1/notifications?limit=$limit&offset=$offset';
       if (unreadOnly) url += '&unread_only=true';
       if (type != null) url += '&type=$type';
       
       final response = await http.get(
         Uri.parse(url),
         headers: {'Authorization': 'Bearer $token'},
       );
       
       if (response.statusCode == 200) {
         final data = json.decode(response.body);
         return (data['notifications'] as List)
             .map((n) => Notification.fromJson(n))
             .toList();
       }
       throw Exception('Failed to load notifications');
     }
     
     Future<int> getUnreadCount() async {
       final token = await getAuthToken();
       
       final response = await http.get(
         Uri.parse('$baseUrl/api/v1/notifications/unread-count'),
         headers: {'Authorization': 'Bearer $token'},
       );
       
       if (response.statusCode == 200) {
         final data = json.decode(response.body);
         return data['unread_count'];
       }
       return 0;
     }
     
     Future<void> markAsRead(int notificationId) async {
       final token = await getAuthToken();
       
       await http.put(
         Uri.parse('$baseUrl/api/v1/notifications/$notificationId/read'),
         headers: {'Authorization': 'Bearer $token'},
       );
     }
     
     Future<void> markAllAsRead() async {
       final token = await getAuthToken();
       
       await http.put(
         Uri.parse('$baseUrl/api/v1/notifications/mark-all-read'),
         headers: {'Authorization': 'Bearer $token'},
       );
     }
   }
   ```

2. UPDATE NOTIFICATION SCREEN
   
   Replace the static notifications in notification_screen.dart with API calls:
   
   ```dart
   class _NotificationScreenState extends State<NotificationScreen> {
     final NotificationService _notificationService = NotificationService();
     List<NotificationItem> _notifications = [];
     bool _isLoading = true;
     
     @override
     void initState() {
       super.initState();
       _loadNotifications();
     }
     
     Future<void> _loadNotifications() async {
       setState(() => _isLoading = true);
       
       try {
         final notifications = await _notificationService.getNotifications();
         setState(() {
           _notifications = notifications;
           _isLoading = false;
         });
       } catch (e) {
         print('Error loading notifications: $e');
         setState(() => _isLoading = false);
       }
     }
     
     // ... rest of the code ...
   }
   ```

DATABASE SCHEMA:
----------------

The notification table should have these columns:

```sql
CREATE TABLE notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'order',
    notification_type VARCHAR(50) DEFAULT 'order',
    is_read BOOLEAN DEFAULT FALSE,
    order_id INTEGER,
    link VARCHAR(500),
    action_url VARCHAR(500),
    image_url VARCHAR(255),
    images JSON,
    metadata JSON,
    actor_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (order_id) REFERENCES "order"(id),
    FOREIGN KEY (actor_user_id) REFERENCES user(id)
);

CREATE INDEX idx_notification_user_id ON notification(user_id);
CREATE INDEX idx_notification_is_read ON notification(is_read);
CREATE INDEX idx_notification_created_at ON notification(created_at);
```

TESTING:
--------

1. Test order flow:
   - Place order → Check buyer and seller notifications
   - Process order → Check buyer notification
   - Ready for pickup → Check buyer and all riders notifications
   - Rider accepts → Check buyer and seller notifications
   - Out for delivery → Check buyer notification
   - Delivered → Check buyer and seller notifications
   - Buyer confirms → Check seller and rider notifications

2. Test API endpoints:
   ```bash
   # Get notifications
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:5000/api/v1/notifications
   
   # Get unread count
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:5000/api/v1/notifications/unread-count
   
   # Mark as read
   curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:5000/api/v1/notifications/1/read
   ```

TROUBLESHOOTING:
----------------

1. Notifications not appearing?
   - Check if notification table exists
   - Check if columns are created (run ensure_notification_table())
   - Check database logs for errors
   - Verify user_id is correct

2. Real-time not working?
   - Check if SocketIO is initialized
   - Check if user is connected to correct room
   - Check browser console for WebSocket errors

3. Mobile app not receiving?
   - Check API endpoint URLs
   - Check authentication token
   - Check network connectivity
   - Check API response in logs

MAINTENANCE:
------------

1. Clean old notifications (run monthly):
   ```python
   from shopee_notification_system import delete_old_notifications
   delete_old_notifications(days=30)
   ```

2. Monitor notification count:
   ```python
   from app import db, Notification
   total = Notification.query.count()
   unread = Notification.query.filter_by(is_read=False).count()
   print(f"Total: {total}, Unread: {unread}")
   ```

SUPPORT:
--------

For issues or questions, check:
- shopee_notification_system.py - Core notification functions
- notification_api_endpoints.py - API endpoints
- app.py - Integration points

Happy coding! 🎉
"""

if __name__ == '__main__':
    print(__doc__)
