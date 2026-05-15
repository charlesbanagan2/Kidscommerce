# Mobile App Quick Start Guide

## ✅ CHANGES COMPLETED

### Landing Page Updated
- **Before**: Login/Register screen on app launch
- **After**: Buyer Home Screen (browse products immediately)

---

## 🚀 HOW TO RUN

### 1. Start Backend Server
```bash
cd C:\Users\mnban\Documents\kids
.venv\Scripts\activate
python backend/app.py
```
Backend will run on: `http://192.168.100.46:5000`

### 2. Run Mobile App
```bash
cd C:\Users\mnban\Documents\kids\mobile_app
flutter run
```

---

## 📱 USER EXPERIENCE

### Guest Mode (No Login Required)
When app launches, users can:
- ✅ Browse all products
- ✅ Search and filter
- ✅ View product details
- ✅ See prices and stock
- ✅ Read reviews

### Login Required For:
- 🔒 Add to cart
- 🔒 Checkout
- 🔒 Place orders
- 🔒 View order history
- 🔒 Leave reviews
- 🔒 Profile management

---

## 🔑 TEST ACCOUNTS

### Buyer Account
- Email: `buyer@test.com`
- Password: `buyer123`

### Seller Account
- Email: `seller@test.com`
- Password: `seller123`

### Rider Account
- Email: `rider@test.com`
- Password: `rider123`

### Admin Account
- Email: `admin@kidscommerce.com`
- Password: `admin123`

---

## 📋 TESTING FLOW

### 1. Guest Browsing
1. Launch app
2. See products immediately
3. Search for products
4. Click on product to view details
5. Try to add to cart → Prompted to login

### 2. Buyer Flow
1. Click "Login" button
2. Login with buyer credentials
3. Browse products
4. Add to cart
5. Proceed to checkout
6. Place order
7. Track order status

### 3. Seller Flow
1. Login with seller credentials
2. View seller dashboard
3. Add new products
4. Manage inventory
5. Process orders

### 4. Rider Flow
1. Login with rider credentials
2. View available deliveries
3. Accept delivery
4. Update delivery status
5. Complete delivery

---

## 🔧 CONFIGURATION

### Backend URL
File: `mobile_app/lib/config/url_config.dart`
```dart
static const String backendHost = '192.168.100.46';
static const int backendPort = 5000;
```

### Network Requirements
- Mobile device must be on same network as backend
- Backend IP: 192.168.100.46
- Backend Port: 5000
- Firewall must allow port 5000

---

## 📚 DOCUMENTATION

- **MOBILE_APP_ANALYSIS.md** - Complete flow documentation
- **LANDING_PAGE_UPDATE.md** - Landing page change details
- **README.md** - Project overview

---

## ✨ KEY FEATURES

### For Buyers
- Browse products without login
- Search and filter
- Add to cart
- Multiple payment methods (COD, GCash, Maya, Card)
- Order tracking
- Product reviews

### For Sellers
- Product management
- Inventory tracking
- Order processing
- Sales analytics

### For Riders
- Delivery management
- Earnings tracking
- Route optimization
- Order status updates

---

## 🐛 TROUBLESHOOTING

### App won't connect to backend
1. Check backend is running: `http://192.168.100.46:5000/api/health`
2. Verify mobile device is on same network
3. Check firewall settings
4. Verify IP address in url_config.dart

### Products not loading
1. Check backend logs
2. Verify Supabase connection
3. Check product status is 'active'
4. Verify stock > 0

### Images not showing
1. Check image files exist in backend/static/uploads/
2. Verify image URLs are correct
3. Check network connectivity

---

## 📞 SUPPORT

For issues or questions:
1. Check documentation files
2. Review backend logs
3. Test API endpoints with TEST_MOBILE.bat
4. Verify Supabase connection

---

## 🎉 SUCCESS!

Your mobile app is now configured to:
✅ Show products immediately on launch
✅ Allow guest browsing
✅ Connect to Supabase via Flask backend
✅ Support Buyer, Seller, and Rider roles
✅ Handle complete e-commerce flow

**Happy Shopping! 🛍️**
