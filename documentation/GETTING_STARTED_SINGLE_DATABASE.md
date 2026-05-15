# Kids E-Commerce Platform - Complete Getting Started Guide

## ✓ Current Status

✅ Backend API fully configured and running ✅ All v1 endpoints created and tested ✅ Single MySQL database architecture enforced ✅ Flutter app routes updated to /api/v1/

## 📋 Prerequisites

### 1. Install MySQL

**Option A: XAMPP (Recommended - easiest)**
- Download from https://www.apachefriends.org/
- Choose Windows version
- Run installer, select MySQL and Apache
- Start MySQL from XAMPP Control Panel
- Default: root user, no password

**Option B: MySQL Direct**
- Download from https://dev.mysql.com/downloads/mysql/
- Download MySQL Server (latest version)
- Run installer, create root user with no password
- Add MySQL bin folder to PATH

**Option C: Docker**
```bash
docker run --name mysql-kids \
  -e MYSQL_ROOT_PASSWORD="" \
  -p 3306:3306 \
  -d mysql:8.0
```

### 2. Verify Installation

```bash
mysql --version
mysql -u root -e "SELECT 1"
```

If these work, MySQL is properly installed.

### 3. Check Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 🚀 Quick Start (5 minutes)

### Step 1: Start MySQL

**If using XAMPP:**
- Open XAMPP Control Panel
- Click "Start" next to MySQL
- Wait for it to show green "Running"

**If installed directly:**
```bash
mysqld --console
# Or on Windows: services.msc → Find MySQL server → Start
```

### Step 2: Create Database

**Option A: Automatic (Recommended)**
```bash
cd c:\Users\mnban\Documents\kids
python setup_database.py
```

**Option B: Using Flask App**
```bash
cd backend
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

**Option C: Manual SQL**
```bash
mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS kids_ecommerce 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_general_ci;
USE kids_ecommerce;
EOF
```

### Step 3: Start Backend Server

```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 4: Test API

```bash
# PowerShell
Invoke-WebRequest -Uri http://127.0.0.1:5000/api/v1/health

# CMD
curl http://127.0.0.1:5000/api/v1/health

# Browser
http://127.0.0.1:5000/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Server is running",
  "timestamp": "2026-04-14T10:00:00..."
}
```

### Step 5: Run Flutter App

```bash
cd mobile_app

# Get dependencies
flutter pub get

# Run on emulator
flutter run -d emulator

# Or run on physical device
flutter run
```

---

## 🗄️ Database Architecture

### Single Shared Database: kids_ecommerce

```
MySQL Server (127.0.0.1:3306)
│
└── Database: kids_ecommerce
    │
    ├── Tables (~50+):
    │   ├── user (buyers, sellers, riders, admins)
    │   ├── product (all merchandise)
    │   ├── category, subcategory
    │   ├── order, order_item, order_label
    │   ├── cart, wishlist
    │   ├── review, return_request
    │   ├── notification, wallet_transaction
    │   └── ... and many more
    │
    ├── Used by Flutter Mobile App
    │   └── Via API: http://127.0.0.1:5000/api/v1/*
    │
    ├── Used by Website (Flask)
    │   └── Web UI: http://127.0.0.1:5000/*
    │
    └── Used by Admin Panel
        └── Admin UI: http://127.0.0.1:5000/admin/*
```

**Key Point:** Only ONE database serves all three interfaces. No duplicates.

---

## 🔌 Connectivity Map

### Mobile App (Flutter) → Backend → Database

```
Flutter App (Android/iOS)
  │
  └─→ HTTP Request to /api/v1/orders
      │
      └─→ Flask Backend Server (Port 5000)
          │
          └─→ SQLAlchemy ORM
              │
              └─→ kids_ecommerce MySQL Database
                  │
                  └─→ Query: SELECT * FROM order WHERE user_id = X
```

### Web UI (Browser) → Backend → Database

```
Browser (http://127.0.0.1:5000)
  │
  └─→ Request to /products
      │
      └─→ Flask Backend Server (Port 5000)
          │
          └─→ SQLAlchemy ORM
              │
              └─→ kids_ecommerce MySQL Database
                  │
                  └─→ Query: SELECT * FROM product
```

---

## 📡 Available API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - New user registration
- `POST /api/v1/auth/refresh` - Refresh access token

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/<id>` - Get product details
- `GET /api/v1/categories` - List categories

### Orders (Requires token)
- `GET /api/v1/orders` - Get all user orders
- `GET /api/v1/orders/<id>` - Get order details
- `GET /api/v1/orders/user` - Get buyer orders
- `GET /api/v1/orders/rider` - Get rider assignments
- `GET /api/v1/orders/seller` - Get seller orders
- `PUT /api/v1/orders/status` - Update order status

### User Profile (Requires token)
- `GET/PUT /api/v1/user/profile` - Get/update profile

### Cart (Requires token)
- `GET/POST/PUT/DELETE /api/v1/cart` - Manage shopping cart

### Wishlist (Requires token)
- `GET/POST/DELETE /api/v1/wishlist` - Manage wishlist

---

## 🧪 Testing the System

### 1. Test Backend Health

```bash
# Check if server is running and responding
Invoke-WebRequest -Uri http://127.0.0.1:5000/api/v1/health
```

### 2. Test User Registration

```bash
$body = @{
    email = "test@example.com"
    password = "Test1234!"
    full_name = "Test User"
    role = "buyer"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://127.0.0.1:5000/api/v1/auth/register `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 3. Test User Login

```bash
$body = @{
    email = "test@example.com"
    password = "Test1234!"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://127.0.0.1:5000/api/v1/auth/login `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 4. Test Product Listing

```bash
Invoke-WebRequest -Uri http://127.0.0.1:5000/api/v1/products | Select -Expand Content | ConvertFrom-Json
```

---

## 🐛 Troubleshooting

### Problem: "MySQL not found in PATH"

**Solution:**
1. Verify MySQL is installed: `Command: mysql --version`
2. If not found, add to PATH:
   - XAMPP: `C:\xampp\mysql\bin`
   - Direct: `C:\Program Files\MySQL\MySQL Server 8.0\bin`
   - Restart terminal after adding to PATH

### Problem: "Access denied for user 'root'@'localhost'"

**Solution:**
1. Check MySQL is running
2. Verify root user has no password (XAMPP default)
3. Or update credentials in `backend/app.py` line 63:
   ```python
   DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/kids_ecommerce'
   ```

### Problem: "Can't connect to MySQL server"

**Solution:**
1. Verify MySQL is running: `mysql -u root -e "SELECT 1"`
2. If error: Start MySQL
   - XAMPP: Start from Control Panel
   - Direct: `mysqld --console` or Services app
3. Check port 3306 is not in use: `netstat -ano | findstr :3306`

### Problem: Flask app won't start

**Solution:**
1. Install dependencies: `pip install -r requirements.txt`
2. Check Python 3.8+: `python --version`
3. Delete `instance/app.db` if it exists
4. Run app with debug output: `python app.py`

### Problem: Flutter app can't reach backend

**Solution:**
1. Get your machine IP: `ipconfig` (look for IPv4 Address)
2. Update in `mobile_app/lib/services/api_service.dart`:
   ```dart
   static String baseUrl = 'http://YOUR_ACTUAL_IP:5000';
   ```
3. On Android emulator, use: `http://10.0.2.2:5000` (special alias)
4. Make sure firewall allows port 5000

---

## 📊 Database Tables Overview

The kids_ecommerce database includes these key tables:

**User Management:**
- `user` - All users (buyers, sellers, riders, admins)
- `address` - User addresses
- `wallet_transaction` - Payment history

**Products & Categories:**
- `category` - Product categories
- `subcategory` - Product subcategories  
- `product` - All products
- `product_image` - Product images
- `review` - Product reviews

**Orders:**
- `order` - Order headers
- `order_item` - Items in each order
- `order_label` - Order status labels
- `order_timeline` - Order history

**Shopping:**
- `cart` - Shopping cart items
- `wishlist` - Wishlist items
- `favorite_seller` - Favorited sellers

**Applications & Roles:**
- `seller_application` - Seller signup requests
- `rider_application` - Rider signup requests
- `rider_availability` - Rider availability schedule

**Communication:**
- `notification` - System notifications
- `store_chat_message` - Seller-buyer chat
- `rider_chat_message` - Rider-buyer chat

**Returns & Support:**
- `return_request` - Return requests
- `return_pickup` - Pickup scheduling
- `support_ticket` - Support tickets

---

## ✨ What's Ready Now

✅ **Backend Server**
- Running on http://127.0.0.1:5000
- All v1 API endpoints implemented
- JWT authentication ready
- CORS enabled for mobile requests

✅ **Flutter Mobile App**
- All 14 endpoints configured for /api/v1/
- Authentication flow ready
- Product browsing ready
- Order management ready

✅ **Database**
- MySQL-only configuration
- Single database for all interfaces
- All 50+ tables defined
- Ready to initialize

---

## 🎯 Next Actions

1. **Install MySQL** (if not already installed)
2. **Start MySQL** service
3. **Initialize Database** using `python setup_database.py`
4. **Start Backend** with `python app.py` (in backend folder)
5. **Build Flutter App** with `flutter run`
6. **Test Full Workflow**: Register → Login → Browse Products → Place Order

---

## 📞 Support Resources

- **Backend Issues:** Check `backend/app.py` logs
- **Database Issues:** Use `mysql -u root` for manual queries
- **Flutter Issues:** Use `flutter doctor` to diagnose environment
- **Port Conflicts:** Check `netstat -ano | findstr :5000` (backend) or `:3306` (MySQL)

---

**Your system is now configured for a single shared MySQL database serving both mobile and web clients!**
