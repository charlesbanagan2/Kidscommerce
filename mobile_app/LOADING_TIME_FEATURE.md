# Loading Time Indicators - Mobile App

## Overview
Added loading time indicators to mobile app, similar to website functionality. Now you can see how long operations take in seconds.

---

## What Was Added

### 1. Performance Monitor Utility
**File:** `lib/utils/performance_monitor.dart`

Tracks timing for all operations:
```dart
PerformanceMonitor.start('Fetch Orders');
// ... operation ...
PerformanceMonitor.end('Fetch Orders'); // Shows: ⏱️ END: Fetch Orders - 1.23s ✅
```

**Features:**
- ⚡ < 0.5s - Very fast
- ✅ < 1.0s - Fast  
- 🟡 < 2.0s - Moderate
- 🟠 < 5.0s - Slow
- 🔴 > 5.0s - Very slow

### 2. Loading Time Widget
**File:** `lib/widgets/loading_time_indicator.dart`

Two ways to show timing:

**A. On-Screen Badge:**
```dart
LoadingTimeIndicator(
  operation: 'Fetch Orders',
  show: true,
)
```

**B. Snackbar Notification:**
```dart
LoadingTimeSnackbar.show(context, 'Fetch Orders');
```

---

## Where It's Used

### Orders Screen
Shows loading time after fetching orders:
```dart
await buyerProvider.fetchOrdersByStatus();
LoadingTimeSnackbar.show(context, 'Fetch Orders');
```

**Example Output:**
```
Console: ⏱️ START: Fetch Orders
Console: ⏱️ END: Fetch Orders - 1.45s ✅
Screen:  [✅ 1.45s] (green snackbar)
```

---

## How to Use

### Step 1: Wrap Operation
```dart
import '../utils/performance_monitor.dart';

Future<void> myOperation() async {
  PerformanceMonitor.start('My Operation');
  
  try {
    // Your code here
    await someApiCall();
    
    PerformanceMonitor.end('My Operation');
  } catch (e) {
    PerformanceMonitor.end('My Operation');
    rethrow;
  }
}
```

### Step 2: Show Result
```dart
// Option A: Snackbar (recommended)
LoadingTimeSnackbar.show(context, 'My Operation');

// Option B: On-screen badge
LoadingTimeIndicator(
  operation: 'My Operation',
  show: true,
)
```

---

## Examples

### Example 1: Fetch Products
```dart
Future<void> fetchProducts() async {
  PerformanceMonitor.start('Fetch Products');
  
  try {
    final products = await ApiService.getProducts();
    PerformanceMonitor.end('Fetch Products');
    
    if (mounted) {
      LoadingTimeSnackbar.show(context, 'Fetch Products');
    }
  } catch (e) {
    PerformanceMonitor.end('Fetch Products');
  }
}
```

**Console Output:**
```
⏱️ START: Fetch Products
⏱️ END: Fetch Products - 0.87s ✅
```

**Screen Output:**
```
[✅ 0.87s] Fetch Products
```

### Example 2: Checkout
```dart
Future<void> checkout() async {
  PerformanceMonitor.start('Checkout');
  
  try {
    final order = await BuyerService.checkout(...);
    PerformanceMonitor.end('Checkout');
    
    LoadingTimeSnackbar.show(context, 'Checkout');
  } catch (e) {
    PerformanceMonitor.end('Checkout');
  }
}
```

### Example 3: Multiple Operations
```dart
// Track multiple operations
PerformanceMonitor.start('Load Cart');
await loadCart();
PerformanceMonitor.end('Load Cart');

PerformanceMonitor.start('Load Products');
await loadProducts();
PerformanceMonitor.end('Load Products');

// Show summary
PerformanceMonitor.printSummary();
```

**Output:**
```
📊 Performance Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Load Products: 1.23s ✅
  Load Cart: 0.45s ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Color Coding

| Time | Emoji | Color | Meaning |
|------|-------|-------|---------|
| < 0.5s | ⚡ | Green | Very fast |
| < 1.0s | ✅ | Light Green | Fast |
| < 2.0s | 🟡 | Orange | Moderate |
| < 5.0s | 🟠 | Deep Orange | Slow |
| > 5.0s | 🔴 | Red | Very slow |

---

## API Reference

### PerformanceMonitor

```dart
// Start timing
PerformanceMonitor.start('Operation Name');

// End timing
PerformanceMonitor.end('Operation Name');

// Get duration
Duration? duration = PerformanceMonitor.getDuration('Operation Name');

// Get formatted string
String time = PerformanceMonitor.getFormattedDuration('Operation Name');

// Clear all
PerformanceMonitor.clear();

// Print summary
PerformanceMonitor.printSummary();

// Measure with wrapper
await PerformanceMonitor.measure('Operation', () async {
  // Your code
});
```

### LoadingTimeIndicator

```dart
LoadingTimeIndicator(
  operation: 'Fetch Orders',  // Required
  show: true,                 // Optional, default true
)
```

### LoadingTimeSnackbar

```dart
LoadingTimeSnackbar.show(
  context,
  'Operation Name',
);
```

---

## Testing

### Run the App:
```bash
cd mobile_app
flutter run
```

### Test Orders Screen:
1. Login as buyer
2. Go to Orders tab
3. Watch console for timing
4. See snackbar with loading time

**Expected Console:**
```
⏱️ START: Fetch Orders
📦 BuyerProvider: Fetching orders by status...
✅ Orders loaded: 5 total orders
⏱️ END: Fetch Orders - 1.23s ✅
```

**Expected Screen:**
```
[✅ 1.23s] Fetch Orders
```

---

## Where to Add More

### Products Screen
```dart
// In products_screen.dart
await buyerProvider.fetchProducts();
LoadingTimeSnackbar.show(context, 'Fetch Products');
```

### Cart Screen
```dart
// In cart_screen.dart
await buyerProvider.fetchCart();
LoadingTimeSnackbar.show(context, 'Fetch Cart');
```

### Checkout Screen
```dart
// In checkout_screen.dart
await buyerProvider.checkout(...);
LoadingTimeSnackbar.show(context, 'Checkout');
```

### Login Screen
```dart
// In login_screen.dart
await authProvider.login(...);
LoadingTimeSnackbar.show(context, 'Login');
```

---

## Benefits

### 1. Performance Monitoring
- See exactly how long operations take
- Identify slow operations
- Track improvements

### 2. User Feedback
- Users see progress
- Transparency about loading times
- Better UX

### 3. Debugging
- Easy to spot performance issues
- Console logs for development
- Visual feedback for testing

---

## Comparison: Website vs Mobile

### Website (Before):
```
Loading products... (shows spinner)
Products loaded! (2.3 seconds)
```

### Mobile (Now):
```
Console: ⏱️ START: Fetch Products
Console: ⏱️ END: Fetch Products - 2.30s 🟡
Screen:  [🟡 2.30s] Fetch Products
```

**Same functionality, same visibility!** ✅

---

## Advanced Usage

### Custom Timing Display
```dart
class MyScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Your content
        
        // Show timing badge
        LoadingTimeIndicator(
          operation: 'Fetch Data',
          show: true,
        ),
      ],
    );
  }
}
```

### Conditional Display
```dart
// Only show if slow
final duration = PerformanceMonitor.getDuration('Fetch Orders');
if (duration != null && duration.inSeconds > 2) {
  LoadingTimeSnackbar.show(context, 'Fetch Orders');
}
```

### Multiple Operations Summary
```dart
// After loading everything
PerformanceMonitor.printSummary();

// Output:
// 📊 Performance Summary:
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//   Fetch Orders: 1.45s ✅
//   Fetch Products: 0.87s ⚡
//   Fetch Cart: 0.34s ⚡
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Summary

✅ **Performance Monitor** - Tracks all operation timings
✅ **Loading Time Widget** - Shows timing on screen
✅ **Snackbar Notifications** - Quick timing feedback
✅ **Color Coded** - Visual speed indicators
✅ **Console Logs** - Development debugging
✅ **Easy to Use** - Simple API
✅ **Same as Website** - Consistent experience

**Now mobile app shows loading times just like the website!** 🎉
