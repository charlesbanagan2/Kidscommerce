# Buyer Mobile App - Quick Start Guide

## 🎯 Overview

Your Kids & Baby Store buyer app is now fully converted to Flutter/Dart. When a buyer logs in through the mobile app, they will be able to access all the features that were previously in HTML:

- ✅ Home Dashboard
- ✅ Shopping Cart
- ✅ Checkout
- ✅ Order Management (with 6 status tabs)
- ✅ Messages (with Sellers & Riders)
- ✅ Profile
- ✅ Returns & Refunds

---

## 🚀 **Quick Setup**

### 1. **Ensure Backend API is Running**
```bash
# From backend directory
python app.py
# or
python run.py
```

**API Base URL:** `http://YOUR_LOCAL_IP:5000/api/v1`

### 2. **Update Mobile API Configuration**

Open `mobile_app/lib/services/api_service.dart`:
```dart
static String baseUrl = 'http://192.168.1.22:5000'; // Change to your IP!
```

### 3. **Update Provider in main.dart**

Ensure BuyerProvider is added:
```dart
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => AuthProvider()),
    ChangeNotifierProvider(create: (_) => BuyerProvider()),
    // ... other providers
  ],
  child: MyApp(),
)
```

### 4. **Run the Flutter App**
```bash
flutter pub get
flutter run
```

---

## 👤 **Buyer Login Flow**

```
1. User launches mobile app
2. Login with email/password
3. Backend validates credentials
4. Returns: user data + JWT tokens
5. App stores tokens in SharedPreferences
6. AuthProvider sets user role = 'buyer'
7. App navigates to → BuyerHomeScreen
8. Uses stored token for subsequent API calls
```

---

## 📱 **Available Screens**

### **Home Screen** (Default)
- Shows quick stats (cart items, pending orders)
- Recent orders preview
- Quick action buttons
- Greeting with user info

### **Orders Tab**
- 6 status categories (To Pay, To Ship, To Receive, Completed, Returns, Cancelled)
- Click any order to view details
- See entire order history

### **Cart Tab**
- View all cart items
- Adjust quantities
- Remove items
- Proceed to checkout

### **Messages Tab**
- Separate tabs for Sellers & Riders
- View conversation history
- Send new messages
- Unread message count

### **Profile Tab**
- View personal info
- Edit profile details
- Update phone/address

---

## 🔌 **API Integration Points**

### **All Buyer Endpoints** (Implemented)

#### Orders
```
GET    /api/v1/buyer/orders              → Get all orders
GET    /api/v1/buyer/orders/by-status    → Get orders grouped by status
GET    /api/v1/buyer/orders/{id}         → Get specific order
POST   /api/v1/buyer/orders/{id}/cancel  → Cancel order
POST   /api/v1/buyer/orders/{id}/confirm-delivery → Confirm receipt
```

#### Cart
```
GET    /api/v1/buyer/cart                → Get cart items
POST   /api/v1/buyer/cart/add            → Add to cart
PUT    /api/v1/buyer/cart/{id}           → Update quantity
DELETE /api/v1/buyer/cart/{id}           → Remove from cart
POST   /api/v1/buyer/cart/clear          → Clear entire cart
```

#### Checkout
```
POST   /api/v1/buyer/checkout            → Create order
POST   /api/v1/buyer/coupon/apply        → Apply coupon code
```

#### Returns
```
GET    /api/v1/buyer/returns             → Get all return requests
GET    /api/v1/buyer/returns/{id}        → Get return details
POST   /api/v1/buyer/orders/{id}/return  → Create return request
```

#### Messages
```
GET    /api/v1/buyer/messages/conversations            → Get all conversations
GET    /api/v1/buyer/messages/{type}/{id}             → Get messages with peer
POST   /api/v1/buyer/messages/send                    → Send message
POST   /api/v1/buyer/messages/{type}/{id}/read        → Mark as read
```

#### Profile
```
GET    /api/v1/buyer/profile             → Get profile
PUT    /api/v1/buyer/profile             → Update profile
POST   /api/v1/buyer/profile/picture     → Update profile picture
```

---

## ✅ **Verification Checklist**

Before going live, verify:

- [ ] **Backend Running:** `http://YOUR_IP:5000` accessible
- [ ] **Database Connected:** MySQL/Maria DB running with buyer data
- [ ] **API Endpoints Working:** Test with Postman
- [ ] **Authentication:** JWT tokens issued on login
- [ ] **CORS Enabled:** Mobile app can reach backend
- [ ] **Flutter App:**
  - [ ] `flutter pub get` completed
  - [ ] No compilation errors
  - [ ] API URL updated to your IP
  - [ ] Test user account created
  - [ ] Can login successfully

### **Quick Test Steps**
1. Run app on physical device or emulator
2. Login with test buyer account (email: buyer@example.com)
3. Check if home screen displays correctly
4. Navigate through all tabs
5. View orders
6. Check cart
7. Test messages

---

## 📊 **Data Flow Diagram**

```
┌─────────────────┐
│  Flutter App    │
│  (Mobile)       │
└────────┬────────┘
         │
    Uses JWT Token
         │
         ↓
┌─────────────────────────────┐
│  Backend API                │
│  GET /api/v1/buyer/*        │
│  POST /api/v1/buyer/*       │
└────────┬────────────────────┘
         │
    SQL Queries
         │
         ↓
┌─────────────────┐
│  MySQL Database │
│  (users, orders,│
│   messages, ...)│
└─────────────────┘
```

---

## 🎨 **Screen Colors & Theme**

- **Primary:** `Colors.purple.shade600` (#8B5CF6)
- **Accent:** `Colors.purple.shade400` (#A78BFA)
- **Success:** Green
- **Warning:** Orange
- **Error:** Red
- **Neutral:** Grey

---

## 🔧 **Troubleshooting**

### **"Connection refused" error**
- ❌ Backend not running
- ✅ Solution: Start Flask backend with `python app.py`

### **"Invalid token" error**
- ❌ Token expired or incorrect
- ✅ Solution: Re-login or check token refresh logic

### **"No route to host" error**
- ❌ IP address incorrect in api_service.dart
- ✅ Solution: Update `baseUrl` with correct IP address

### **"CORS error" error**
- ❌ Backend CORS not configured
- ✅ Solution: Ensure CORS headers in Flask (already added)

### **Empty orders/cart display**
- ❌ API returning empty data
- ✅ Solution: Check database has buyer data

---

## 📚 **File Reference**

### Core Files (Already Implemented)
```
lib/models/order.dart                    - Data models
lib/services/buyer_service.dart         - API client
lib/providers/buyer_provider.dart       - State management

lib/screens/buyer_app/
├── buyer_home_screen.dart              - Home & navigation
├── cart_screen.dart                    - Shopping cart
├── checkout_screen.dart                - Order checkout
├── orders_screen.dart                  - Order list with tabs
├── order_detail.dart                   - Order details
├── messages_screen.dart                - Messaging
├── profile_screen.dart                 - User profile
└── returns_index.dart                  - Returns/Refunds
```

---

## 🚀 **Next Steps**

1. **Test the app** on physical device
2. **Verify all API calls** work correctly
3. **Check database** for proper data
4. **Test edge cases** (empty states, errors)
5. **Optimize performance** if needed
6. **Deploy to production**

---

## 💡 **Key Features Implemented**

✅ **Order Management**
- View all orders with status filtering
- Track order progress
- Cancel pending orders
- Confirm delivery

✅ **Shopping Experience**
- Add/remove cart items
- Adjust quantities
- Apply coupon codes
- Checkout flow

✅ **Communication**
- Real-time messaging with sellers
- Message history
- Unread message badges

✅ **User Profile**
- View personal information
- Edit profile details
- Profile picture

✅ **Return Management**
- Request returns for completed orders
- Upload media (photos/videos)
- Track return status

---

## 📞 **Support**

For issues or questions:
1. Check API logs: `backend/app.log` (if enabled)
2. Check mobile logs: `flutter logs`
3. Review error messages in app
4. Check database for data integrity

---

**Status:** ✅ Complete & Ready for Testing
**Last Updated:** April 15, 2026

Enjoy your new Flutter buyer app! 🎉
