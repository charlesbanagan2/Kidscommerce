# 🚀 QUICK START - Shopee-Style Notification System

## Mabilis na Pag-install (5 Minutes)

### Step 1: Run Integration Script
```bash
cd backend
python integrate_notifications.py
```

Ito ay automatic na:
- ✅ Mag-create ng backup ng app.py
- ✅ Mag-add ng notification imports
- ✅ Mag-add ng notification calls sa lahat ng order endpoints
- ✅ Mag-setup ng API endpoints

### Step 2: Restart Backend
```bash
python app.py
```

### Step 3: Test Notifications

#### Test via Web Browser:
1. Login as buyer
2. Place an order
3. Check notifications sa header (bell icon)

#### Test via API:
```bash
# Get your auth token first (login via mobile app or web)
TOKEN="your_jwt_token_here"

# Get notifications
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/notifications

# Get unread count
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/v1/notifications/unread-count
```

---

## 📱 Mobile App Integration (Flutter)

### Step 1: Create Notification Service

Create file: `lib/services/notification_service.dart`

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import '../utils/auth_storage.dart';

class NotificationService {
  Future<Map<String, dynamic>> getNotifications({
    int limit = 50,
    int offset = 0,
    bool unreadOnly = false,
  }) async {
    final token = await AuthStorage.getToken();
    
    var url = '${ApiConfig.baseUrl}/api/v1/notifications?limit=$limit&offset=$offset';
    if (unreadOnly) url += '&unread_only=true';
    
    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load notifications');
  }
  
  Future<int> getUnreadCount() async {
    final token = await AuthStorage.getToken();
    
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/api/v1/notifications/unread-count'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['unread_count'] ?? 0;
    }
    return 0;
  }
  
  Future<void> markAsRead(int notificationId) async {
    final token = await AuthStorage.getToken();
    
    await http.put(
      Uri.parse('${ApiConfig.baseUrl}/api/v1/notifications/$notificationId/read'),
      headers: {'Authorization': 'Bearer $token'},
    );
  }
  
  Future<void> markAllAsRead() async {
    final token = await AuthStorage.getToken();
    
    await http.put(
      Uri.parse('${ApiConfig.baseUrl}/api/v1/notifications/mark-all-read'),
      headers: {'Authorization': 'Bearer $token'},
    );
  }
}
```

### Step 2: Update Notification Screen

Replace the `_notifications` list in `notification_screen.dart`:

```dart
class _NotificationScreenState extends State<NotificationScreen> {
  final NotificationService _notificationService = NotificationService();
  List<NotificationItem> _notifications = [];
  bool _isLoading = true;
  NotificationFilter _activeFilter = NotificationFilter.all;
  
  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }
  
  Future<void> _loadNotifications() async {
    setState(() => _isLoading = true);
    
    try {
      final response = await _notificationService.getNotifications();
      final notificationsList = response['notifications'] as List;
      
      setState(() {
        _notifications = notificationsList.map((json) {
          return NotificationItem(
            id: json['id'].toString(),
            title: json['title'] ?? 'Notification',
            message: json['message'] ?? '',
            time: _formatTime(json['created_at']),
            type: _getNotificationType(json['type']),
            isRead: json['is_read'] ?? false,
          );
        }).toList();
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading notifications: $e');
      setState(() => _isLoading = false);
    }
  }
  
  NotificationType _getNotificationType(String? type) {
    switch (type) {
      case 'order':
        return NotificationType.order;
      case 'promotion':
        return NotificationType.promotion;
      case 'product':
        return NotificationType.product;
      default:
        return NotificationType.order;
    }
  }
  
  String _formatTime(String? timestamp) {
    if (timestamp == null) return 'Just now';
    
    try {
      final dateTime = DateTime.parse(timestamp);
      final now = DateTime.now();
      final difference = now.difference(dateTime);
      
      if (difference.inMinutes < 1) return 'Just now';
      if (difference.inMinutes < 60) return '${difference.inMinutes} minutes ago';
      if (difference.inHours < 24) return '${difference.inHours} hours ago';
      if (difference.inDays < 7) return '${difference.inDays} days ago';
      return '${(difference.inDays / 7).floor()} weeks ago';
    } catch (e) {
      return 'Just now';
    }
  }
  
  // ... rest of your existing code ...
}
```

### Step 3: Add Pull-to-Refresh

```dart
@override
Widget build(BuildContext context) {
  return Scaffold(
    backgroundColor: _AppColors.background,
    body: RefreshIndicator(
      onRefresh: _loadNotifications,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: CustomScrollView(
          // ... existing code ...
        ),
      ),
    ),
  );
}
```

---

## ✅ Verification Checklist

### Backend Verification:
- [ ] `integrate_notifications.py` ran successfully
- [ ] `app.py` has notification imports
- [ ] Backend starts without errors
- [ ] API endpoints respond (test with curl)

### Database Verification:
```python
# Run in Python shell
from app import app, db, Notification
with app.app_context():
    count = Notification.query.count()
    print(f"Total notifications: {count}")
```

### Mobile App Verification:
- [ ] NotificationService created
- [ ] notification_screen.dart updated
- [ ] App compiles without errors
- [ ] Notifications load from API

---

## 🎯 Test Scenarios

### Scenario 1: Place Order
1. Login as buyer
2. Add product to cart
3. Checkout
4. **Expected:** Buyer and seller receive notifications

### Scenario 2: Process Order
1. Login as seller
2. Go to orders
3. Click "Process Order"
4. **Expected:** Buyer receives "Order Processing" notification

### Scenario 3: Rider Delivery
1. Login as rider
2. Accept available order
3. Mark as delivered
4. **Expected:** Buyer receives "Order Delivered" notification

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found: shopee_notification_system"
**Solution:**
```bash
# Make sure files are in backend directory
ls -la shopee_notification_system.py
ls -la notification_api_endpoints.py
```

### Issue: "Notification table doesn't exist"
**Solution:**
```python
# Run in Python shell
from app import app, db
from shopee_notification_system import ensure_notification_table

with app.app_context():
    ensure_notification_table()
```

### Issue: Mobile app shows "Failed to load notifications"
**Solution:**
1. Check API URL in `api_config.dart`
2. Check authentication token
3. Check backend logs for errors
4. Test API with curl first

---

## 📊 Monitoring

### Check Notification Stats:
```python
from app import app, db, Notification

with app.app_context():
    total = Notification.query.count()
    unread = Notification.query.filter_by(is_read=False).count()
    by_type = db.session.query(
        Notification.type,
        db.func.count(Notification.id)
    ).group_by(Notification.type).all()
    
    print(f"Total: {total}")
    print(f"Unread: {unread}")
    print(f"By type: {dict(by_type)}")
```

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Notifications appear in database
- ✅ API endpoints return data
- ✅ Mobile app shows notifications
- ✅ Real-time updates work (via SocketIO)
- ✅ Unread count updates correctly

---

## 📚 Additional Resources

- **Full Guide:** `NOTIFICATION_SYSTEM_COMPLETE_TAGALOG.md`
- **Integration Guide:** `SHOPEE_NOTIFICATION_INTEGRATION_GUIDE.py`
- **Core Functions:** `shopee_notification_system.py`
- **API Endpoints:** `notification_api_endpoints.py`

---

## 🆘 Need Help?

1. Check the full documentation
2. Review the integration guide
3. Test with curl commands
4. Check backend logs
5. Check mobile app logs

---

**That's it! Your Shopee-style notification system is ready! 🎉**

Time to test: Place an order and watch the notifications flow! 🚀
