# Rider Profile API Call Optimization

## Issue
Excessive API calls to `/api/v1/chat/unread-count` and `/api/v1/notifications/unread-count` causing:
- Performance issues (frame skipping)
- Unnecessary network traffic
- Repeated identical API calls every few seconds

## Root Causes

### 1. **rider_home_screen.dart** - Aggressive Polling
- Timer was set to 30 seconds interval
- Called unread count API on every tab switch to messages
- No debouncing or throttling mechanism

### 2. **rider_dashboard_screen.dart** - Inefficient Data Fetching
- Fetched ALL notifications just to count unread ones
- Called on every dashboard refresh/load
- Transferred unnecessary data (full notification objects instead of just count)

## Fixes Applied

### 1. rider_home_screen.dart
**Before:**
```dart
_refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
  _fetchUnreadCounts();
});

void _onTap(int i) {
  // ...
  if (i == 3) _fetchUnreadCounts(); // Messages tab
}
```

**After:**
```dart
_refreshTimer = Timer.periodic(const Duration(minutes: 2), (_) {
  if (mounted) _fetchUnreadCounts();
});

void _onTap(int i) {
  // Removed redundant call on tab switch
}
```

**Changes:**
- Increased polling interval from 30 seconds to 2 minutes (4x reduction)
- Added mounted check to prevent calls after widget disposal
- Removed redundant API call when switching to messages tab

### 2. rider_dashboard_screen.dart
**Before:**
```dart
final notifResponse = await ApiService.getNotifications();
if (notifResponse['success'] == true) {
  final notifications = notifResponse['notifications'] as List? ?? [];
  _unreadNotificationCount =
      notifications.where((n) => n['is_read'] == false).length;
}
```

**After:**
```dart
// Use unread count API instead of fetching all notifications
final unreadCount = await ApiService.getUnreadNotificationsCount();
_unreadNotificationCount = unreadCount;
```

**Changes:**
- Replaced `getNotifications()` with `getUnreadNotificationsCount()`
- Reduced data transfer (count vs full notification objects)
- Faster response time
- Less server load

## Performance Impact

### Before:
- API calls every 30 seconds from home screen
- Full notification list fetched on every dashboard load
- Multiple redundant calls on tab switches
- ~120+ API calls per hour

### After:
- API calls every 2 minutes from home screen
- Only unread count fetched (minimal data)
- No redundant calls on tab switches
- ~30 API calls per hour (75% reduction)

## Additional Benefits

1. **Reduced Network Usage**: Fetching count instead of full objects saves bandwidth
2. **Better Battery Life**: Fewer API calls = less radio usage
3. **Improved Performance**: No frame skipping from excessive network activity
4. **Server Load Reduction**: 75% fewer requests to backend

## Testing Recommendations

1. Monitor logs for API call frequency
2. Verify unread counts still update correctly
3. Check that notification badge updates within 2 minutes
4. Test on slow network connections
5. Verify no memory leaks from timer

## Future Improvements

Consider implementing:
1. **WebSocket/Push Notifications**: Real-time updates instead of polling
2. **Exponential Backoff**: Increase interval when no new notifications
3. **Smart Polling**: Only poll when app is in foreground
4. **Local Caching**: Cache counts with TTL to reduce API calls further
