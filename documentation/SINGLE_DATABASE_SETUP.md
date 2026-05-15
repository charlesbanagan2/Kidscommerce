# Single Database Configuration - MySQL Only
# For both Mobile App and Website

## Database Setup

### Windows/Local Setup
```bash
# 1. Install MySQL (via XAMPP, Docker, or MySQL Installer)
# XAMPP Control Panel: Start MySQL service

# 2. Create the single database
mysql -u root -p
# Enter password (usually empty for XAMPP)

CREATE DATABASE kids_ecommerce;
USE kids_ecommerce;

# 3. Run the comprehensive update script
source database_update_comprehensive.sql;

# Exit MySQL
exit;
```

### Environment Configuration
File: `.env` or `backend/app.py` defaults

```env
# Single MySQL database for both mobile and web
DATABASE_URI=mysql+pymysql://root:@127.0.0.1:3306/kids_ecommerce
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=kids_ecommerce

# JWT Configuration
JWT_SECRET_KEY=your-mobile-jwt-secret-key-change-in-production

# Email Configuration
MAIL_SENDER=ccody7313@gmail.com
MAIL_APP_PASSWORD=ecjdfangradrblcl
```

## Architecture

### Single Database Setup
```
🗄️ MySQL Database: kids_ecommerce
    ├── Tables: 30+
    ├── On: 127.0.0.1:3306
    └── Access by:
        ├── Mobile App (via Flask API)
        ├── Website (via Flask API + Templates)
        └── Admin Panel (direct)
```

### Application Architecture
```
┌─────────────────────────────────────────────────────┐
│         Single kids_ecommerce Database              │
│  (MySQL - Shared by all applications)               │
└─────────────────────────────────────────────────────┘
                        ▲
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────▼────┐  ┌─────▼──────┐  ┌───▼────┐
    │  Flask  │  │   Flask    │  │ Flask  │
    │ API v1  │  │   Web UI   │  │ Admin  │
    │ (Port   │  │ (Port 5000)│  │Panel   │
    │ 5000)   │  │            │  │(5000)  │
    └────┬────┘  └─────┬──────┘  └───┬────┘
         │              │              │
    ┌────▼──────────────▼──────────────▼────┐
    │    Flask Backend (Single Instance)     │
    │    - JWT Authentication                │
    │    - Role-Based Access Control         │
    │    - CRUD Operations                   │
    │    - WebSocket (Socket.IO)             │
    └─────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐  ┌─────▼──────┐  ┌───▼────┐
    │ Flutter │  │  Web App   │  │ Admin  │
    │ Mobile  │  │ (Browser)  │  │Web UI  │
    │   App   │  │            │  │        │
    └─────────┘  └────────────┘  └────────┘
```

## Data Flow

### Mobile App
```
Flutter App (10.0.2.2:5000 or 192.168.100.46:5000)
    ↓
REST API Calls (/api/v1/*)
    ↓
Flask Backend (localhost:5000)
    ↓
Single MySQL Database (127.0.0.1:3306)
```

### Website & Admin
```
Web Browser (localhost:5000)
    ↓
Flask Routes (/ /admin /dashboard)
    ↓
Flask Backend (localhost:5000)
    ↓
Single MySQL Database (127.0.0.1:3306)
```

## Shared Tables

Both mobile and web access the same 30+ tables:

### Core Tables
- `user` - All users (buyer, seller, rider, admin)
- `seller_application` - Seller applications
- `rider_application` - Rider applications
- `product` - Products from sellers
- `category` - Product categories
- `subcategory` - Product subcategories

### Transaction Tables
- `order` - Orders from buyers
- `order_item` - Items in each order
- `order_label` - QR codes and tracking
- `cart` - Shopping cart items
- `coupon` - Discount coupons
- `wallet_transaction` - Earnings and payments

### Communication Tables
- `notification` - In-app notifications
- `store_chat_message` - Buyer-Seller chat
- `rider_chat_message` - Buyer-Rider chat

### Management Tables
- `return_request` - Returns and refunds
- `restock_request` - Inventory requests
- `return_pickup` - Rider pickup tasks
- `delivery_personnel` - Delivery staff
- `qr_scan_log` - QR code tracking

### Configuration Tables
- `theme_setting` - Site branding
- `hero_slide` - Homepage banners
- `admin_profile` - Admin settings
- `admin_security_log` - Audit logs
- `address` - User addresses
- `follow` - Seller followers
- `review` - Product reviews
- `wishlist` - Saved products
- `oauth` - Google OAuth records
- `region` - PSGC regions
- `province` - PSGC provinces
- `city` - PSGC cities
- `barangay` - PSGC barangays
- `city_municipality` - PSGC city/municipality

## Backup & Restore

### Backup Single Database
```bash
# Full backup
mysqldump -u root -p kids_ecommerce > backup_kids_ecommerce.sql

# Schedule daily backups (Windows Task Scheduler)
mysqldump -u root kids_ecommerce > "C:\backups\kids_ecommerce_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.sql"
```

### Restore from Backup
```bash
mysql -u root -p kids_ecommerce < backup_kids_ecommerce.sql
```

## Performance Tips

### Single Database Best Practices
1. ✅ Use indexes on frequently queried columns
2. ✅ Enable connection pooling (already configured)
3. ✅ Set appropriate timeouts
4. ✅ Regular backups
5. ✅ Monitor database size
6. ✅ Archive old orders periodically

### Current Configuration (app.py)
```python
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,      # Test connections
    'pool_recycle': 3600,        # Recycle every hour
    'pool_timeout': 30,          # 30 sec timeout
    'connect_args': {
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60
    }
}
```

## Verification

### Check Database Connection
```python
# Python Shell
python
>>> from app import app, db
>>> with app.app_context():
...     result = db.session.execute('SELECT 1')
...     print("✅ Single database connected")
>>> exit()
```

### List All Tables
```bash
mysql -u root -p kids_ecommerce -e "SHOW TABLES;"
```

### Check Database Size
```bash
mysql -u root -p kids_ecommerce -e "SELECT 
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)' 
    FROM information_schema.tables 
    WHERE table_schema = 'kids_ecommerce';"
```

## Migration Path

If you currently have separate databases:

```bash
# 1. Backup all separate databases
mysqldump -u root database_1 > backup_1.sql
mysqldump -u root database_2 > backup_2.sql

# 2. Create single database
mysql -u root -p
CREATE DATABASE kids_ecommerce;

# 3. Merge data (if needed)
mysql -u root kids_ecommerce < backup_1.sql
mysql -u root kids_ecommerce < backup_2.sql

# 4. Run comprehensive update
mysql -u root kids_ecommerce < database_update_comprehensive.sql

# 5. Update backend configuration to use single database
# Edit backend/.env or app.py
DATABASE_URI=mysql+pymysql://root:@127.0.0.1:3306/kids_ecommerce

# 6. Restart Flask backend
python app.py
```

## Summary

✅ **Single Database:** `kids_ecommerce` (MySQL)
✅ **Both Mobile & Web:** Use same database via Flask API
✅ **No SQLite Fallback:** MySQL only
✅ **Connection Pool:** Optimized for concurrent access
✅ **Shared Schema:** All tables in one database
✅ **Real-time Sync:** Changes visible immediately to both apps

---

**Status:** Single database configuration ready
**Database:** kids_ecommerce (MySQL)
**Accessed By:** Mobile app + Website + Admin Panel (all via Flask)
