# Debug Information for Order Detail Screen

## Check These Things:

### 1. Run the app and open an order detail
Look at the console output for these debug messages:
```
🔍 Order Status: [status_value]
🔍 Rider ID: [rider_id_value]
🔍 Rider Name: [rider_name_value]
🔍 Rider Phone: [rider_phone_value]
```

### 2. Expected Button Behavior:

**For status = 'to_receive':**
- ✅ Should show: "Order Received" (green button)
- ✅ Should show: "Return & Refund" (orange outline button)
- ❌ Should NOT show: "Chat with Rider"
- ❌ Should NOT show: "Rate Now"

**For status = 'delivered' OR 'completed':**
- ✅ Should show: "Rate Now" (blue button) ONLY
- ❌ Should NOT show: "Order Received"
- ❌ Should NOT show: "Return & Refund"
- ❌ Should NOT show: "Chat with Rider"

**For status = 'to_pay':**
- ✅ Should show: "Pay Now" (blue button)
- ✅ Should show: "Cancel Order" (red outline button)

### 3. Rider Info Card:

**Should display when:**
- `order.riderName` is NOT null
- `order.riderName` is NOT empty string

**Should show:**
- Rider name (without "Rider Name:" label)
- Rider phone number (without "Phone Number:" label) - if available

### 4. Common Issues:

**If buttons are not showing:**
1. Check the debug output - what is the actual order status?
2. The status might be something unexpected like:
   - `out_for_delivery` instead of `to_receive`
   - `pending` instead of `to_pay`
   - Different casing (e.g., `To_Receive` vs `to_receive`)

**If rider info is not showing:**
1. Check debug output for rider name and phone
2. Backend might not be sending rider data
3. Rider might not be assigned to the order yet

### 5. Quick Fix Test:

To test if buttons work at all, temporarily change line 1145 to:
```dart
if (true)  // Force show button for testing
```

This will show the button regardless of status, confirming the button rendering works.
