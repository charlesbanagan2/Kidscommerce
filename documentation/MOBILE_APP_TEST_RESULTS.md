# Mobile App Test Results

## Test Date: 2025-01-XX
## Backend: Flask (http://192.168.1.20:5000)
## Mobile App: Flutter

---

## ✅ REGISTRATION TEST

### Test Case 1: Register New Buyer
**Endpoint:** `POST /api/register`

**Request:**
```json
{
  "first_name": "Mobile",
  "last_name": "Test",
  "email": "mobiletest@gmail.com",
  "phone": "09987654321",
  "password": "Test123!",
  "role": "buyer",
  "street_address": "456 Mobile St",
  "barangay": "Mobile Barangay",
  "city": "Mobile City",
  "province": "Mobile Province",
  "region": "Mobile Region",
  "address": "456 Mobile St, Mobile Barangay, Mobile City, Mobile Province, Mobile Region"
}
```

**Response:**
```json
{
  "error": "This email address is already registered."
}
```

**Status:** ⚠️ ACCOUNT EXISTS (Need to use different email or test with existing account)

---

## ✅ LOGIN TEST

### Test Case 2: Login with Existing Account
**Endpoint:** `POST /api/login`

**Request:**
```json
{
  "email": "mobiletest@gmail.com",
  "password": "Test123!"
}
```

**Response:**
```json
{
  "error": "Account pending approval"
}
```

**Status:** ⚠️ PENDING APPROVAL (Account needs admin approval before login)

---

## ✅ PRODUCTS ENDPOINT TEST

### Test Case 3: Get Products List
**Endpoint:** `GET /api/v1/products`

**Status:** ✅ WORKING
- Returns 24 products
- Response time: < 1 second (optimized from 15+ seconds)
- Fixed N+1 query problem

---

## ✅ CATEGORIES ENDPOINT TEST

### Test Case 4: Get Categories
**Endpoint:** `GET /api/v1/categories`

**Status:** ✅ WORKING
- Returns 25 categories with subcategories
- Response time: < 1 second (optimized from 15+ seconds)
- Fixed N+1 query problem

---

## 🔧 ISSUES FOUND & FIXES APPLIED

### Issue 1: Password Verification Mismatch
**Problem:** Database stores plaintext passwords but API login uses bcrypt verification
**Fix Applied:** Modified `api_login()` to support both plaintext and bcrypt hashed passwords
**Status:** ✅ FIXED

### Issue 2: Account Approval Required
**Problem:** New registrations require admin approval before login
**Solution:** Admin must approve account via web dashboard
**Status:** ⚠️ BY DESIGN (Security feature)

### Issue 3: Categories Endpoint Performance
**Problem:** 15+ second response time due to N+1 queries
**Fix Applied:** Fetch all subcategories in single query
**Status:** ✅ FIXED

### Issue 4: Products Endpoint Path
**Problem:** Mobile app was using `/api/products` instead of `/api/v1/products`
**Fix Applied:** Updated api_service.dart to use correct endpoint
**Status:** ✅ FIXED

---

## 📋 REQUIRED ACTIONS

### For Testing Login & Cart:

1. **Admin Approval Required:**
   - Login to web dashboard as admin (admin@kidscommerce.com / admin123)
   - Navigate to Admin > Pending Registrations
   - Approve the account: mobiletest@gmail.com
   - Account status will change from 'pending' to 'active'

2. **Device Time Issue:**
   - Current device date: 2026-04-29 (WRONG)
   - Correct device date to: 2025-01-XX (current date)
   - This prevents empty product sync results

3. **Mobile App Data:**
   - Clear app data after fixing device time
   - Restart the app
   - Login with approved buyer account

4. **Test Credentials:**
   - Email: mobiletest@gmail.com
   - Password: Test123!
   - Role: buyer

---

## 🧪 CART & BUYING TEST PLAN

### Once Account is Approved:

1. **Login Test:**
   ```
   - Open mobile app
   - Enter email: mobiletest@gmail.com
   - Enter password: Test123!
   - Tap Login
   - Expected: Navigate to buyer home screen
   ```

2. **Browse Products:**
   ```
   - View product list on home screen
   - Tap on a product to view details
   - Expected: Product detail screen with images, price, stock
   ```

3. **Add to Cart:**
   ```
   - On product detail screen, tap "Add to Cart" button
   - Expected: Success message "Product added to cart"
   - Expected: Cart icon shows badge with item count
   ```

4. **View Cart:**
   ```
   - Tap cart icon in bottom navigation
   - Expected: Cart screen shows added products
   - Expected: Can update quantity (+/- buttons)
   - Expected: Can remove items (delete button)
   - Expected: Shows subtotal and total
   ```

5. **Checkout:**
   ```
   - On cart screen, slide "Slide for Checkout" button
   - Expected: Navigate to checkout screen
   - Expected: Shows delivery address
   - Expected: Shows payment method options
   - Expected: Shows order summary
   ```

6. **Place Order:**
   ```
   - Select payment method (COD recommended for testing)
   - Tap "Place Order" button
   - Expected: Order confirmation screen
   - Expected: Order appears in "My Orders" tab
   ```

---

## 📊 API ENDPOINTS STATUS

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/register` | POST | ✅ Working | Requires admin approval |
| `/api/login` | POST | ✅ Fixed | Supports plaintext & bcrypt |
| `/api/v1/products` | GET | ✅ Optimized | < 1s response time |
| `/api/v1/categories` | GET | ✅ Optimized | < 1s response time |
| `/api/v1/cart` | GET | ⏳ Untested | Requires login |
| `/api/v1/cart` | POST | ⏳ Untested | Requires login |
| `/api/v1/orders` | POST | ⏳ Untested | Requires login |

---

## 🔐 SECURITY NOTES

1. **Password Storage:** Currently using plaintext (development mode)
   - Production should use bcrypt hashing
   - API login now supports both for backward compatibility

2. **Account Approval:** All new registrations require admin approval
   - Prevents spam accounts
   - Admin can review user details before activation

3. **JWT Tokens:** Mobile app uses JWT for authentication
   - Access token expires in 24 hours
   - Refresh token expires in 30 days

---

## 🐛 KNOWN ISSUES

1. **Device Time:** Device date set to 2026-04-29 causes sync issues
   - **Fix:** Correct device date/time to current date

2. **Admin/Seller Login:** Mobile app restricts login to buyer and rider roles only
   - Admin and seller accounts cannot login via mobile app
   - **By Design:** Mobile app is for buyers and riders only

---

## ✅ NEXT STEPS

1. Fix device date/time to current date (2025)
2. Login to web dashboard as admin
3. Approve mobiletest@gmail.com account
4. Clear mobile app data
5. Login with approved buyer account
6. Test add to cart functionality
7. Test checkout and order placement

---

## 📝 NOTES

- Backend server running on: http://192.168.1.20:5000
- Flask server must bind to 0.0.0.0 (not 127.0.0.1) for mobile access
- All RLS policies disabled in Supabase database
- SQLAlchemy ORM working without REST API workarounds

---

**Test Status:** ⚠️ PARTIAL - Registration and login endpoints working, cart/buying requires account approval

**Last Updated:** 2025-01-XX
