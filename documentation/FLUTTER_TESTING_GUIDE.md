# Flutter Mobile App - Testing Guide

## Quick Start

### Prerequisites
- Flutter SDK installed
- Android emulator running (or device connected)
- Backend Flask server running at `http://192.168.1.20:5000`

### Build & Run

```bash
cd c:\Users\mnban\Documents\kids\mobile_app

# Clean build
flutter clean

# Get dependencies
flutter pub get

# Run on Android emulator/device
flutter run
```

---

## Testing Workflow

### 1. Login Test
**Test Account (Buyer)**:
- Email: `matt@gmail.com`
- Password: `030904Jeff!`

**Expected Result**:
- Successful login
- Navigated to `BuyerHomeScreen`
- No error messages

---

### 2. Product Browsing Test

**From BuyerHomeScreen**:
1. Look for "Featured Products" carousel
2. Scroll through featured products
3. Should show 24 products from API

**From ProductListingScreen** (if navigation added):
1. Tap on "View All Products" button (if added)
2. Should display:
   - 2-column grid of products
   - Category filter chips at top
   - Search bar
   - Sort dropdown
   - All 24 products visible

**Test Features**:
- [ ] **Search**: Type "baby" - should filter products
- [ ] **Categories**: Tap different categories - products filtered
- [ ] **Sort**: Select "Price: Low to High" - products reordered
- [ ] **Grid**: Products display in clean 2-column layout
- [ ] **Images**: All product images load correctly
- [ ] **Stock**: Out-of-stock items show properly

---

### 3. Product Detail Test

**From ProductListingScreen**:
1. Tap any product card
2. Should navigate to `ProductDetailScreen`

**Expected UI Elements**:
- [ ] Product image at top
- [ ] Product name below image
- [ ] Rating stars (0-5) with review count
- [ ] Price in large text, sale price with strikethrough
- [ ] Stock status (green "In Stock" or red "Out of Stock")
- [ ] Seller info card with store icon
- [ ] Full product description
- [ ] Quantity selector (+/- buttons)
- [ ] "Add to Cart" button (enabled if in stock)
- [ ] "Buy Now" button (currently placeholder)

**Test Actions**:
- [ ] Increase/decrease quantity
- [ ] Click "Add to Cart" - shows snackbar confirmation
- [ ] Try "Buy Now" - shows placeholder message

---

### 4. Shopping Cart Test

**After Adding Products**:
1. Navigate to Cart screen (via navigation/bottom nav)
2. Should show:
   - [ ] Added product with correct name
   - [ ] Correct quantity
   - [ ] Correct price
   - [ ] Total price at bottom
   - [ ] Remove button to delete item
   - [ ] Quantity adjustment controls

**Test Actions**:
- [ ] Update product quantity - total updates
- [ ] Remove product - item disappears
- [ ] Continue Shopping - returns to ProductListingScreen
- [ ] Checkout - navigates to checkout screen

---

### 5. Rider Dashboard Test

**Switch Account to Rider** (if test account available):
1. Logout from current account
2. Login with rider credentials
3. Should navigate to `RiderDashboardScreen` (not BuyerHomeScreen)

**Expected UI**:
- [ ] Summary cards showing earnings, completed, active
- [ ] Tabbed interface (Active, Completed, Pending)
- [ ] Delivery cards showing:
   - Order ID
   - Status badge (color-coded)
   - Customer name
   - Delivery address
   - Order amount
   - Action buttons
   - Call button

**Test Tabs**:
- [ ] **Active Tab**: Shows 3 mock deliveries
- [ ] **Completed Tab**: Shows 1 mock delivery
- [ ] **Pending Tab**: Shows 1 mock delivery

**Test Buttons**:
- [ ] Accept button on pending delivery
- [ ] Complete button on active delivery
- [ ] Call button on any delivery (shows snackbar)

---

### 6. Role-Based Navigation Test

**Test Correct Screen Based on Role**:

1. **Buyer Login**:
   - email: `matt@gmail.com`
   - Expected: BuyerHomeScreen

2. **Rider Login** (if available):
   - Expected: RiderDashboardScreen

3. **Non-Buyer/Rider Login**:
   - Expected: Error message "Seller accounts cannot use this app"
   - Stays on login screen

---

## Network Testing

### Verify Backend Connectivity
```bash
# From PC, test if backend is accessible
curl http://192.168.1.20:5000/api/products

# Should return JSON with 24 products
```

### Android Emulator Network
- Android emulator can reach 192.168.1.20:5000 directly
- No special configuration needed

### Physical Device Testing
- Connect Android device to same WiFi network as backend
- Ensure 192.168.1.20 is accessible from device
- Test with: `adb shell ping 192.168.1.20`

---

## Common Issues & Fixes

### Issue: "No products displayed"
**Cause**: Backend not running or unreachable
**Fix**:
1. Start Flask backend: `python app.py`
2. Verify backend is at `192.168.1.20:5000`
3. Check Android device can reach it: `adb shell ping 192.168.1.20`

### Issue: "Login fails with 401"
**Cause**: Using non-buyer/non-rider account
**Fix**: Use credentials: matt@gmail.com / 030904Jeff!

### Issue: "Images not loading"
**Cause**: Product image URLs missing backend prefix
**Fix**: Verify BuyerProvider adds full URL:
```dart
String imageUrl = productJson['image'] ?? '';
if (imageUrl.isNotEmpty && !imageUrl.startsWith('http')) {
  imageUrl = 'http://192.168.1.20:5000$imageUrl';
}
```

### Issue: "App crashes on product tap"
**Cause**: ProductDetailScreen not imported
**Fix**: Ensure import in product_listing_screen.dart:
```dart
import 'product_detail_screen.dart';
```

---

## Debug Tools

### View Flutter Logs
```bash
flutter logs
```

### Run with Debug Info
```bash
flutter run -v
```

### Check Device Connection
```bash
adb devices
```

### Inspect Widget Tree
- Use Flutter DevTools: `flutter pub global run devtools`
- Open in browser: `http://localhost:6100`

---

## Performance Testing

### Expected Load Times
- App startup: < 2 seconds
- Product list load: < 1 second (from API cache)
- Product detail load: < 500ms
- Search filter: < 200ms
- Sort operation: < 100ms

### Monitor Network
- Open Network tab in DevTools
- Check requests to `192.168.1.20:5000`
- Verify response codes (200 for success)

---

## Data Verification

### Database Products
- Total products: 24
- Product fields: id, name, description, price, sale_price, image, category, stock, rating, review_count, seller_id, seller_name

### Test Product
```json
{
  "id": 1,
  "name": "Baby Bottle",
  "price": 299.99,
  "sale_price": 199.99,
  "image": "/static/products/bottle.jpg",
  "category": "Baby Care",
  "stock": 15,
  "rating": 4.5,
  "review_count": 23
}
```

### Categories Available
- Baby Care
- Clothing
- Gear
- (Check `/api/products` response for full list)

---

## Success Criteria

### ✅ All Tests Passing If:
1. ✅ Login successful with valid credentials
2. ✅ Buyer navigates to BuyerHomeScreen
3. ✅ ProductListingScreen shows 24 products
4. ✅ Search/filter/sort all work
5. ✅ ProductDetailScreen displays complete info
6. ✅ Add to cart works and shows confirmation
7. ✅ Cart screen shows added items
8. ✅ Rider can login and see RiderDashboardScreen
9. ✅ All images load without errors
10. ✅ No crashes or unhandled exceptions

---

## Next Testing Phase

After basic functionality verified:
1. Test checkout flow (Buy Now → Payment)
2. Test order history/tracking
3. Test rider delivery status updates
4. Test search with special characters
5. Test with poor network conditions
6. Test with 100+ products (load performance)
7. Stress test with rapid API calls
