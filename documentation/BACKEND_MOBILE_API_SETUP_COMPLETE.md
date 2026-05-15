# Backend Mobile API Setup - COMPLETE ✅

## System Status

**Backend Server:** Running ✅
- **Local URL:** http://127.0.0.1:5000
- **Network URL:** http://192.168.100.46:5000
- **Health Check:** http://127.0.0.1:5000/api/v1/health

---

## Completed Tasks

### 1. **Flutter API Client Routes Updated** ✅
All 14 API endpoint routes in [lib/services/api_service.dart](lib/services/api_service.dart) updated:
- ✅ Base URL: `http://10.0.2.2:5000` (Android emulator) → Configure for physical device
- ✅ Authentication: `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/refresh`
- ✅ Products: `/api/v1/products`, `/api/v1/products/<id>`
- ✅ Cart: `/api/v1/cart` (GET, POST, PUT, DELETE)
- ✅ Orders: `/api/v1/orders`, `/api/v1/orders/<id>`, `/api/v1/orders/user`, `/api/v1/orders/rider`, `/api/v1/orders/status`
- ✅ Health: `/api/v1/health`

### 2. **Missing Backend v1 Endpoints Created** ✅
Added 5 new v1 endpoints to [backend/app.py](backend/app.py):

#### `/api/v1/health` (NEW)
```
GET /api/v1/health
Response: { "status": "ok", "message": "Server is running", "timestamp": "2026-04-14T09:58:03.978390" }
```
Tests database connectivity and server health.

#### `/api/v1/orders/user` (NEW)
```
GET /api/v1/orders/user?status=<optional_status>
Authorization: Bearer <access_token>
Role Required: buyer
Response: { "success": true, "orders": [...] }
```
Returns buyer's orders with optional status filtering.

#### `/api/v1/orders/rider` (NEW)
```
GET /api/v1/orders/rider
Authorization: Bearer <access_token>
Role Required: rider
Response: { "success": true, "orders": [...customer_info...] }
```
Returns rider's assigned/completed orders with customer details.

#### `/api/v1/orders/seller` (NEW)
```
GET /api/v1/orders/seller?status=<optional_status>
Authorization: Bearer <access_token>
Role Required: seller
Response: { "success": true, "orders": [...] }
```
Returns seller's orders containing their products.

#### `/api/v1/orders/status` (NEW)
```
PUT /api/v1/orders/status
Authorization: Bearer <access_token>
Content-Type: application/json
Body: {
  "order_id": 123,
  "status": "processing|ready_for_pickup|picked_up|delivered|cancelled",
  "rider_id": <optional>
}
Role Required: seller|rider|admin
Response: { "success": true, "order": {...} }
```
Updates order status with role-based permissions.

### 3. **Backend API v1 Endpoints Verification** ✅
Confirmed all existing v1 endpoints are working:
- ✅ POST `/api/v1/auth/login`
- ✅ POST `/api/v1/auth/register`
- ✅ POST `/api/v1/auth/refresh`
- ✅ GET `/api/v1/products`
- ✅ GET `/api/v1/products/<id>`
- ✅ GET/POST `/api/v1/orders`
- ✅ GET `/api/v1/orders/<id>`
- ✅ GET/PUT `/api/v1/user/profile`
- ✅ GET `/api/v1/categories`
- ✅ GET/POST/PUT/DELETE `/api/v1/cart`
- ✅ GET/POST/DELETE `/api/v1/wishlist`

---

## API Authentication Flow

### 1. **Register (New User)**
```
POST /api/v1/auth/register
{ 
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@gmail.com",
  "password": "SecurePass123!",
  "phone": "09123456789",
  "address": "Manila, Philippines",
  "role": "buyer"
}
Response: {
  "success": true,
  "user": {...},
  "access_token": "eyJ0eXAi...",
  "refresh_token": "refresh_token_value",
  "expires_in": 86400
}
```

### 2. **Login (Existing User)**
```
POST /api/v1/auth/login
{
  "email": "john@gmail.com",
  "password": "SecurePass123!"
}
Response: {
  "success": true,
  "user": {...},
  "access_token": "eyJ0eXAi...",
  "refresh_token": "refresh_token_value",
  "expires_in": 86400
}
```

### 3. **Authenticated Requests**
All subsequent requests require Bearer token in Authorization header:
```
GET /api/v1/user/profile
Authorization: Bearer eyJ0eXAi...
Content-Type: application/json
```

### 4. **Token Refresh**
When access token expires (24 hours), refresh it:
```
POST /api/v1/auth/refresh
{
  "refresh_token": "refresh_token_value"
}
Response: {
  "success": true,
  "access_token": "new_access_token",
  "expires_in": 86400
}
```

---

## Role-Based Access Control

### Buyer Role
- Register and login
- Browse products and categories
- Manage cart and wishlist
- Place orders
- View own orders (GET `/api/v1/orders/user`)
- Leave product reviews
- Return/refund requests

### Rider Role
- Accept delivery jobs (GET `/api/v1/orders/rider`)
- Update delivery status (`/api/v1/orders/status`)
- Track pickup and delivery timestamps
- Communicate with buyers

### Seller Role
- Register company/store
- Upload and manage products
- View own orders containing their products
- Update order status to `processing` or `ready_for_pickup`
- Manage inventory and pricing

### Admin Role
- Approve/reject user registrations
- Approve/reject seller applications
- Approve/reject products
- Manage categories and coupons
- View all orders and transactions
- Full system administration

---

## Environment Configuration

### Backend Configuration (backend/.env or defaults)
```
DATABASE_URI=mysql+pymysql://root:@127.0.0.1:3306/kids_ecommerce
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=kids_ecommerce

JWT_SECRET_KEY=your-mobile-jwt-secret-key-change-in-production
MAIL_SENDER=ccody7313@gmail.com
```

### Flutter Configuration (lib/services/api_service.dart)
```dart
// Development (Android Emulator)
static String baseUrl = 'http://10.0.2.2:5000';

// For physical device (replace with your machine IP)
static String baseUrl = 'http://192.168.100.46:5000';
```

---

## Database Setup

### Option 1: MySQL (Recommended for Production)
```bash
# Ensure MySQL is running and create database
mysql -u root -p
CREATE DATABASE kids_ecommerce;
CREATE DATABASE kids_ecommerce_test;
```

### Option 2: SQLite (Development)
Backend automatically falls back to SQLite if MySQL is unavailable.

### Create Database Tables
```python
# Run from Flask shell
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

---

## Testing the API

### 1. **Health Check**
```bash
# Test if backend is running
curl http://127.0.0.1:5000/api/v1/health
# or
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/v1/health" -Method GET
```

### 2. **Register Test User**
```bash
# Create a buyer account
POST http://127.0.0.1:5000/api/v1/auth/register
{
  "first_name": "TestBuyer",
  "last_name": "Account",
  "email": "testbuyer@gmail.com",
  "password": "TestPass123!",
  "phone": "09123456789",
  "address": "Test Address",
  "role": "buyer"
}
```

### 3. **Login and Get Token**
```bash
# Login to get access token
POST http://127.0.0.1:5000/api/v1/auth/login
{
  "email": "testbuyer@gmail.com",
  "password": "TestPass123!"
}
# Save the access_token returned
```

### 4. **Fetch Products**
```bash
GET http://127.0.0.1:5000/api/v1/products?page=1&per_page=10
Authorization: Bearer <access_token_from_login>
```

### 5. **Get Buyer Orders**
```bash
GET http://127.0.0.1:5000/api/v1/orders/user
Authorization: Bearer <access_token>
```

---

## Flutter App Next Steps

### 1. **Update BaseURL for Your Device**

**For Android Emulator (Keep as-is):**
```dart
// lib/services/api_service.dart
static String baseUrl = 'http://10.0.2.2:5000';
```

**For Physical Device/iPhone Simulator:**
Replace `10.0.2.2` with your machine's IP address:
```dart
static String baseUrl = 'http://192.168.100.46:5000'; // Use YOUR IP
```

Find your IP:
```bash
# Windows PowerShell
Get-NetIPAddress -AddressFamily IPv4 | Where {$_.AddressState -eq "Preferred"}

# Or check network settings
ipconfig

# Mac/Linux
ifconfig
```

### 2. **Build and Run Flutter App**
```bash
# Navigate to Flutter project
cd mobile_app

# Get dependencies
flutter pub get

# Run on Android Emulator
flutter run -d emulator

# Run on physical device
flutter run

# Run with verbose logging for debugging
flutter run -v
```

### 3. **Test Authentication Flow**
1. Open the app
2. Register new account or login
3. Verify tokens are stored in SharedPreferences
4. Navigate to buyer/rider/seller screens based on role
5. Test cart, orders, and other features

### 4. **Debug API Calls**
Enable debug logging in api_service.dart:
```dart
print('API Request: $method $endpoint');
print('Headers: $headers');
print('Response: ${response.body}');
```

---

## Common Issues & Solutions

### Issue 1: "Connection refused" on Flutter
**Solution:** 
- Check backend is running: `curl http://127.0.0.1:5000/api/v1/health`
- Verify baseUrl matches your network (10.0.2.2 for emulator, your IP for physical device)
- Check firewall allows port 5000

### Issue 2: "Invalid token" errors
**Solution:**
- Token may have expired (24 hour expiry)
- Use `/api/v1/auth/refresh` to get new token
- Check token is sent in Authorization header as `Bearer <token>`

### Issue 3: "Cannot authenticate" with valid credentials
**Solution:**
- Check email/password are exactly correct (case-sensitive)
- Verify user account status is `active` (not `pending` or `rejected`)
- Admin must approve registration before login possible

### Issue 4: Database connection errors
**Solution:**
- For MySQL: Verify MySQL service is running and database `kids_ecommerce` exists
- For SQLite: Backend creates database.db automatically, check write permissions
- Check DATABASE_URI in environment or app.py defaults

---

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2026-04-14T09:58:03.978390"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "status": 400,
  "timestamp": "2026-04-14T09:58:03.978390"
}
```

---

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in Flask
- [ ] Generate strong `JWT_SECRET_KEY`
- [ ] Configure proper database (MySQL on production server)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for actual domain
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up environment variables for sensitive data
- [ ] Configure email service for notifications
- [ ] Set up logging and monitoring
- [ ] Test all API endpoints thoroughly
- [ ] Implement rate limiting
- [ ] Backup database regularly

---

## Summary

✅ **Backend API is fully operational** with all v1 endpoints for Flutter integration:
- 5 new order endpoints (`/orders/user`, `/orders/rider`, `/orders/seller`, `/orders/status`, `/health`)
- JWT authentication with 24-hour expiry
- Role-based access control (buyer, rider, seller, admin)
- SQLite fallback for development
- Full error handling and logging
- CORS enabled for mobile app

**Next Step:** Build and test Flutter app against running backend server.

**Backend Server Running On:**
- Development: http://127.0.0.1:5000
- Network: http://192.168.100.46:5000
- Health Check: http://127.0.0.1:5000/api/v1/health

---

**Last Updated:** 14 Apr 2026 10:00 UTC
**Status:** ✅ PRODUCTION READY FOR TESTING
