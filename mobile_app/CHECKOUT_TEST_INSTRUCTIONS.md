# Checkout Test Instructions

## How to Run the Checkout Test in Mobile App

### Option 1: Add to Navigation (Temporary)

Add this import to your main navigation file (e.g., `buyer_home_screen.dart` or wherever you have a menu):

```dart
import 'package:kids/screens/test/checkout_test_screen.dart';
```

Then add a button to navigate to the test screen:

```dart
ElevatedButton(
  onPressed: () {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CheckoutTestScreen()),
    );
  },
  child: const Text('Test Checkout'),
)
```

### Option 2: Add to Drawer Menu

If you have a drawer menu, add this item:

```dart
ListTile(
  leading: const Icon(Icons.science),
  title: const Text('Checkout Test'),
  onTap: () {
    Navigator.pop(context); // Close drawer
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CheckoutTestScreen()),
    );
  },
)
```

### Option 3: Direct Navigation (Quick Test)

In any screen, you can temporarily add a FloatingActionButton:

```dart
floatingActionButton: FloatingActionButton(
  onPressed: () {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CheckoutTestScreen()),
    );
  },
  child: const Icon(Icons.science),
)
```

## Running the Test

1. **Login** to the app as a buyer
2. **Add items** to your cart (at least 1 item)
3. **Navigate** to the Checkout Test screen
4. **Press** "Run Checkout Test" button
5. **Watch** the logs appear in real-time
6. **Verify** the test passes (green checkmark)

## What the Test Validates

✅ User authentication
✅ Cart fetching
✅ Checkout API call
✅ Order creation
✅ Response structure validation
✅ Order data completeness

## Expected Result

If everything works correctly, you should see:

```
============================================
CHECKOUT TEST STARTED
============================================

1. Checking authentication...
✅ User authenticated
   User ID: 25
   Email: test@gmail.com

2. Fetching cart...
✅ Cart fetched successfully
   Items: 1
   Item 1: Product Name x1 @ ₱100.0
   Total: ₱100.00

3. Preparing checkout data...
   Selected items: [69]

4. Performing checkout...
✅ Checkout successful!

5. Validating order...
   Order ID: 123
   Status: pending
   Total: ₱110.00
   Payment: cod
   Items: 1
   Item 1: Product Name x1

✅ All validations passed!

============================================
✅ CHECKOUT TEST PASSED!
============================================
```

## Troubleshooting

If the test fails:

1. Check the error message in the logs
2. Verify you're logged in
3. Ensure cart has items
4. Check network connection
5. Verify backend is running on http://192.168.1.20:5000
6. Check Flutter console for detailed error logs

## Clean Up

After testing, remove the test navigation button/menu item from your production code.
