# Mobile App Cart & Buying Functionality Test

## Prerequisites
1. ✅ Backend server running on http://192.168.1.20:5000
2. ⚠️ Test account needs admin approval
3. ⚠️ Device date must be corrected (currently 2026-04-29)

---

## Test Account Setup

### Option 1: Use Existing Account (Recommended)
If you have an existing approved buyer account, use those credentials.

### Option 2: Approve Test Account
1. Login to web dashboard: http://192.168.1.20:5000/login
   - Email: admin@kidscommerce.com
   - Password: admin123

2. Navigate to: Admin > Pending Registrations

3. Find and approve: mobiletest@gmail.com

4. Test credentials:
   - Email: mobiletest@gmail.com
   - Password: Test123!

---

## Manual Test Flow

### Step 1: Login ✅
```
Endpoint: POST /api/login
Request:
{
  "email": "mobiletest@gmail.com",
  "password": "Test123!"
}

Expected Response:
{
  "message": "Login successful",
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 86400
  },
  "user": {
    "id": X,
    "email": "mobiletest@gmail.com",
    "first_name": "Mobile",
    "last_name": "Test",
    "role": "buyer"
  }
}
```

### Step 2: Get Products ✅
```
Endpoint: GET /api/v1/products
Headers: Authorization: Bearer {access_token}

Expected: List of 24 products with:
- id, name, description, price
- image_url, stock, category
- seller information
```

### Step 3: Get Cart (Empty Initially)
```
Endpoint: GET /api/v1/cart
Headers: Authorization: Bearer {access_token}

Expected Response:
{
  "cart": {
    "items": [],
    "total": 0,
    "item_count": 0
  }
}
```

### Step 4: Add Product to Cart
```
Endpoint: POST /api/v1/cart
Headers: 
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request:
{
  "product_id": 1,
  "quantity": 2
}

Expected Response:
{
  "success": true,
  "message": "Product added to cart",
  "cart": {
    "items": [
      {
        "id": X,
        "product_id": 1,
        "product_name": "Product Name",
        "price": 100.00,
        "quantity": 2,
        "subtotal": 200.00,
        "image_url": "/static/uploads/..."
      }
    ],
    "total": 200.00,
    "item_count": 1
  }
}
```

### Step 5: Update Cart Quantity
```
Endpoint: PUT /api/v1/cart/{cart_item_id}
Headers: 
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request:
{
  "quantity": 3
}

Expected Response:
{
  "success": true,
  "message": "Cart updated",
  "cart": {
    "items": [...],
    "total": 300.00,
    "item_count": 1
  }
}
```

### Step 6: Get Updated Cart
```
Endpoint: GET /api/v1/cart
Headers: Authorization: Bearer {access_token}

Expected: Cart with updated quantities and totals
```

### Step 7: Checkout (Create Order)
```
Endpoint: POST /api/v1/orders
Headers: 
  Authorization: Bearer {access_token}
  Content-Type: application/json

Request:
{
  "shipping_address": "789 Cart St, Cart Barangay, Cart City, Cart Province, Cart Region",
  "payment_method": "COD",
  "notes": "Test order from mobile app"
}

Expected Response:
{
  "success": true,
  "message": "Order placed successfully",
  "order": {
    "id": X,
    "order_number": "ORD-XXXXX",
    "total_amount": 300.00,
    "status": "pending",
    "payment_method": "COD",
    "payment_status": "pending",
    "shipping_address": "...",
    "created_at": "2025-01-XX...",
    "items": [
      {
        "product_id": 1,
        "product_name": "...",
        "quantity": 3,
        "price": 100.00,
        "subtotal": 300.00
      }
    ]
  }
}
```

### Step 8: Get Orders
```
Endpoint: GET /api/v1/orders
Headers: Authorization: Bearer {access_token}

Expected: List of orders including the newly created one
```

### Step 9: Get Order Details
```
Endpoint: GET /api/v1/orders/{order_id}
Headers: Authorization: Bearer {access_token}

Expected: Full order details with items, status, tracking info
```

---

## API Endpoints Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/login` | POST | No | Login and get tokens |
| `/api/v1/products` | GET | Yes | Get product list |
| `/api/v1/cart` | GET | Yes | Get current cart |
| `/api/v1/cart` | POST | Yes | Add item to cart |
| `/api/v1/cart/{id}` | PUT | Yes | Update cart item quantity |
| `/api/v1/cart/{id}` | DELETE | Yes | Remove item from cart |
| `/api/v1/orders` | POST | Yes | Create order (checkout) |
| `/api/v1/orders` | GET | Yes | Get user's orders |
| `/api/v1/orders/{id}` | GET | Yes | Get order details |

---

## Mobile App Test Steps

### 1. Fix Device Date
- Go to Settings > Date & Time
- Change from 2026-04-29 to current date (2025-01-XX)
- Restart device

### 2. Clear App Data
- Go to Settings > Apps > Kids Commerce
- Clear Storage/Data
- Restart app

### 3. Login
- Open app
- Enter email: mobiletest@gmail.com (or your approved account)
- Enter password: Test123!
- Tap Login
- ✅ Should navigate to home screen

### 4. Browse Products
- View product grid on home screen
- Scroll through products
- Tap on a product
- ✅ Should show product detail screen

### 5. Add to Cart
- On product detail screen
- Tap "Add to Cart" button
- ✅ Should show success message
- ✅ Cart badge should show "1"

### 6. View Cart
- Tap cart icon in bottom navigation
- ✅ Should show cart screen with added product
- ✅ Should show quantity controls (+/-)
- ✅ Should show subtotal and total

### 7. Update Quantity
- Tap + button to increase quantity
- ✅ Quantity should increase
- ✅ Subtotal should update
- ✅ Total should update

### 8. Remove Item (Optional)
- Tap delete/trash icon
- ✅ Item should be removed
- ✅ Cart should update

### 9. Add Multiple Products
- Go back to home
- Add 2-3 different products
- ✅ Cart badge should show correct count
- ✅ Cart should show all items

### 10. Checkout
- On cart screen
- Slide "Slide for Checkout" button
- ✅ Should navigate to checkout screen
- ✅ Should show delivery address
- ✅ Should show payment methods

### 11. Place Order
- Select payment method (COD recommended)
- Review order summary
- Tap "Place Order"
- ✅ Should show order confirmation
- ✅ Should show order number
- ✅ Cart should be empty

### 12. View Orders
- Tap "Orders" in bottom navigation
- ✅ Should show list of orders
- ✅ New order should appear at top
- ✅ Should show order status

### 13. View Order Details
- Tap on the order
- ✅ Should show full order details
- ✅ Should show items, quantities, prices
- ✅ Should show delivery address
- ✅ Should show order status

---

## Expected Behavior

### Cart Functionality
- ✅ Add products to cart
- ✅ Update quantities
- ✅ Remove items
- ✅ Calculate subtotals and totals
- ✅ Persist cart across app restarts
- ✅ Show cart badge with item count

### Checkout Functionality
- ✅ Select delivery address
- ✅ Choose payment method
- ✅ Review order summary
- ✅ Place order
- ✅ Clear cart after successful order
- ✅ Show order confirmation

### Order Management
- ✅ View order history
- ✅ View order details
- ✅ Track order status
- ✅ Cancel pending orders (if implemented)

---

## Common Issues & Solutions

### Issue 1: "Account pending approval"
**Solution:** Admin must approve account via web dashboard

### Issue 2: "Token is invalid or expired"
**Solution:** Login again to get new tokens

### Issue 3: Empty product list
**Solution:** 
- Check device date (must be current date, not 2026)
- Clear app data and restart

### Issue 4: "Product out of stock"
**Solution:** Choose a different product with available stock

### Issue 5: Cart not updating
**Solution:**
- Check network connection
- Verify backend server is running
- Check API response for errors

---

## Backend Verification

### Check Cart in Database
```sql
SELECT * FROM cart WHERE user_id = X;
```

### Check Orders in Database
```sql
SELECT * FROM "order" WHERE buyer_id = X ORDER BY created_at DESC;
```

### Check Order Items
```sql
SELECT oi.*, p.name 
FROM order_item oi 
JOIN product p ON oi.product_id = p.id 
WHERE oi.order_id = X;
```

---

## Test Results Template

### Login Test
- [ ] Can login with approved account
- [ ] Receives valid JWT tokens
- [ ] Tokens work for authenticated requests

### Cart Test
- [ ] Can view empty cart
- [ ] Can add products to cart
- [ ] Can update quantities
- [ ] Can remove items
- [ ] Cart totals calculate correctly
- [ ] Cart badge shows correct count

### Checkout Test
- [ ] Can view checkout screen
- [ ] Can select delivery address
- [ ] Can choose payment method
- [ ] Can place order successfully
- [ ] Cart clears after order
- [ ] Order confirmation shows

### Order Test
- [ ] Can view order list
- [ ] Can view order details
- [ ] Order status displays correctly
- [ ] Can track order

---

## Next Steps

1. **Approve test account** via web dashboard
2. **Fix device date** to current date
3. **Clear app data** and restart
4. **Follow test steps** above
5. **Document results** using template
6. **Report any issues** found

---

**Test Status:** ⏳ READY TO TEST (Pending account approval and device date fix)

**Last Updated:** 2025-01-XX
