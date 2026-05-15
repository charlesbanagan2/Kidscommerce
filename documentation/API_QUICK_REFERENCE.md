# Quick API Testing Reference

## Backend Server Status
✅ **Running on:** http://192.168.100.46:5000
✅ **Health Check:** http://127.0.0.1:5000/api/v1/health

## All v1 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/register` - Register new user  
- `POST /api/v1/auth/refresh` - Refresh expired access token

### Products
- `GET /api/v1/products` - List all products with pagination
- `GET /api/v1/products/<id>` - Get product details

### Orders (NEW)
- `GET /api/v1/orders` - List all orders (admin only)
- `POST /api/v1/orders` - Create new order (buyer)
- `GET /api/v1/orders/<id>` - Get order details
- `GET /api/v1/orders/user` - Get buyer's orders (requires buyer token)
- `GET /api/v1/orders/rider` - Get rider's orders (requires rider token)
- `GET /api/v1/orders/seller` - Get seller's orders (requires seller token)
- `PUT /api/v1/orders/status` - Update order status (seller/rider/admin)

### Cart
- `GET /api/v1/cart` - Get cart items
- `POST /api/v1/cart` - Add item to cart
- `PUT /api/v1/cart` - Update cart item quantity
- `DELETE /api/v1/cart` - Remove item from cart

### User Profile
- `GET /api/v1/user/profile` - Get current user profile
- `PUT /api/v1/user/profile` - Update user profile

### Lists
- `GET /api/v1/categories` - Get product categories
- `GET /api/v1/wishlist` - Get wishlist items
- `POST /api/v1/wishlist` - Add to wishlist
- `DELETE /api/v1/wishlist` - Remove from wishlist

### Health
- `GET /api/v1/health` - Check server health (NEW)

---

## Test Workflow

### 1. Register Buyer Account
```
POST http://192.168.100.46:5000/api/v1/auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Buyer",
  "email": "johnbuyer@gmail.com",
  "password": "TestPass123!",
  "phone": "09123456789",
  "address": "123 Test Street",
  "role": "buyer"
}

Response:
{
  "success": true,
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 86400
}
```

### 2. Login with Email/Password
```
POST http://192.168.100.46:5000/api/v1/auth/login
Content-Type: application/json

{
  "email": "johnbuyer@gmail.com",
  "password": "TestPass123!"
}

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Buyer",
    "email": "johnbuyer@gmail.com",
    "role": "buyer",
    "status": "active"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 86400
}
```

### 3. Get Buyer Orders (with token)
```
GET http://192.168.100.46:5000/api/v1/orders/user
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

Response:
{
  "success": true,
  "orders": [
    {
      "id": 123,
      "buyer_id": 1,
      "total_amount": 5999.99,
      "status": "pending",
      "created_at": "2026-04-14T10:00:00",
      ...
    }
  ]
}
```

### 4. Refresh Expired Token
```
POST http://192.168.100.46:5000/api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "success": true,
  "access_token": "new_token_here",
  "expires_in": 86400
}
```

---

## Flutter Configuration

### Update lib/services/api_service.dart

**For Android Emulator:**
```dart
static String baseUrl = 'http://10.0.2.2:5000';
```

**For Physical Device (CHANGE THIS):**
```dart
static String baseUrl = 'http://192.168.100.46:5000'; // Your machine IP
```

To find your IP:
```bash
# Windows
ipconfig

# Mac/Linux  
ifconfig

# Look for IPv4 Address: 192.168.x.x or similar
```

---

## Running Flutter App

### Android Emulator
```bash
cd mobile_app
flutter run -d emulator
```

### Physical Device
```bash
flutter run
# Select device when prompted
```

### With Debug Logging
```bash
flutter run -v
```

---

## Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK - Request successful | ✅ Continue |
| 201 | Created - Resource created | ✅ Success |
| 400 | Bad Request - Invalid data | ❌ Check request format |
| 401 | Unauthorized - Invalid/missing token | ❌ Login again or refresh token |
| 403 | Forbidden - Don't have permission | ❌ Wrong role for action |
| 404 | Not Found - Resource doesn't exist | ❌ Check ID/endpoint |
| 500 | Server Error | ❌ Check backend logs |
| 503 | Service Unavailable - DB down | ❌ Check database connection |

---

## Token Management

### Access Token
- **Duration:** 24 hours
- **Usage:** Include in Authorization header for API calls
- **Format:** `Authorization: Bearer <token>`
- **When Expires:** Use refresh token to get new one

### Refresh Token  
- **Duration:** 30 days
- **Usage:** Exchange for new access token
- **Endpoint:** POST `/api/v1/auth/refresh`

### Token Storage (Flutter)
```dart
// SharedPreferences
await _prefs.setString('access_token', token);
await _prefs.setString('refresh_token', refreshToken);

// Retrieve for API calls
String? token = _prefs.getString('access_token');
```

---

## Important Notes

⚠️ **Server IP:** 192.168.100.46 is YOUR specific machine IP. Update if different.

⚠️ **Port 5000:** Must not be in use. Stop other services if needed.

⚠️ **Password Requirements:**
- 8-12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter  
- At least 1 number
- At least 1 special character (!@#$%^&*-_)

⚠️ **CORS:** Backend allows requests from any origin for development. Restrict in production.

⚠️ **Database:** Using SQLite for development (database.db file in backend/)

---

## Debugging Tips

### Check Health
```bash
curl http://127.0.0.1:5000/api/v1/health
```

### View Backend Logs
Server logs appear in terminal where you ran `python app.py`

### Test with NO Token (Should Fail)
```bash
GET http://192.168.100.46:5000/api/v1/orders/user
# Response: 401 Unauthorized
```

### Register Multiple Test Users
You can make different roles for testing:
- Buyer: `role: "buyer"`
- Rider: `role: "rider"` 
- Seller: `role: "seller"`
- Admin: Skip registration, use admin account directly

### Admin Direct Login
```
Email: admin@kidscommerce.com
Password: Admin123!
(Auto-creates on first login with correct password)
```

---

**Last Updated:** 14 Apr 2026
**Status:** ✅ Ready for Mobile App Testing
