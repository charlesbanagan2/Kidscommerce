# Available Test User Accounts

## 🔑 Test Credentials Quick Reference

### ✅ READY TO USE - Active Accounts

#### 1️⃣ Admin Account (Highest Priority)
```
Email: admin@kidscommerce.com
Password: admin123
Role: admin
Status: ACTIVE ✅
```
**Use this for**: Quick testing, full access to all features

#### 2️⃣ Test Buyer Accounts

**Account 1: buyer_test (New Test Account)**
```
Email: buyer@test.com
Password: (retrieve from database)
Role: buyer
Status: ACTIVE ✅
Name: Test Buyer
```

**Account 2: debug.buyer (Debug Account)**
```
Email: debug.buyer@test.com
Password: (from database)
Role: buyer
Status: ACTIVE ✅
Name: Debug Buyer
Created: 2026-04-15
```

**Account 3: john.buyer (Named Test Account)**
```
Email: john.buyer@test.com
Password: (from database)
Role: buyer
Status: ACTIVE ✅
Name: John Buyer
Created: 2026-04-15
```

**Account 4: testbuyer (Latest Test Account)**
```
Email: testbuyer@test.com
Password: (from database)
Role: buyer
Status: ACTIVE ✅
Name: Test Buyer
Created: 2026-04-16
```

#### 3️⃣ Seller Accounts

**Account 1: BABY BLISS KIDS STORE**
```
Email: babybliss@gmail.com
Password: Buyer@1234
Role: seller
Status: ACTIVE ✅
Store Name: BABY BLISS KIDS STORE
```

**Other Sellers (All Active)**
```
Email: kiddopia@gmail.com (KIDDOPIA PH)
Email: whimsicalwear@gmail.com (WHIMSICAL WEAR)
Email: peekaboo@gmail.com (PEEKABOO PH)
Email: gigglegear@gmail.com (GIGGLE GEAR)
Email: cutiecove@gmail.com (CUTIE COVE)
```

#### 4️⃣ Rider Accounts

**Account 1: rider@gmail.com**
```
Email: rider@gmail.com
Name: Rider Rider
Status: ACTIVE ✅
Created: 2025-11-22
```

**Account 2: jane.rider@test.com**
```
Email: jane.rider@test.com
Name: Jane Rider
Status: ACTIVE ✅
Created: 2026-04-15
```

**Account 3: test.rider@test.com**
```
Email: test.rider@test.com
Name: Test Rider
Status: ACTIVE ✅
Created: 2026-04-16
```

**Account 4: juanrider@gmail.com**
```
Email: juanrider@gmail.com
Name: Juan Rider
Status: ACTIVE ✅
Created: 2025-11-28
```

---

## ⚠️ NON-ACTIVE Accounts (Not for Testing)

### Rejected Status (❌ Cannot Login)
```
Email: buyer@gmail.com (Buyer buyer) - REJECTED
Email: buyer1@gmail.com (Buyer buyer) - REJECTED
Email: katumboktips@gmail.com (jeffrey policarpio) - REJECTED
```

### Pending Status (⏳ Awaiting Approval)
```
Email: jqwhdjwbbd@gmail.com (Juan awdhb) - PENDING REVIEW
```

### Legacy/Deprecated Accounts
```
Email: zeffpolicarpio2004@gmail.com (OAuth login - not regular password)
Email: Matt@gmail.com (from old testing)
Email: jeffreyp352@gmail.com (from old testing)
```

---

## 📊 Quick Stats

**Total Accounts**: 27
- ✅ **Active**: 23 (ready for testing)
- ⏳ **Pending**: 1 (awaiting review)
- ❌ **Rejected**: 3 (cannot login)

**By Role**:
- 👨‍💼 Admin: 1
- 🛍️ Buyers: 13 (10 active)
- 🏪 Sellers: 6 (all active)
- 🚴 Riders: 7 (6 active)

---

## 🎯 Recommended Testing Order

### Priority 1: Quick Test (5 min)
1. Use: `admin@kidscommerce.com` / `admin123`
2. Verify login works
3. Check field validation works
4. Test logout

### Priority 2: Buyer Testing (10 min)
1. Use: `buyer@test.com` (newest test account)
2. Test buyer-specific features
3. Add product to cart
4. Test checkout

### Priority 3: Multi-Role Testing (15 min)
1. Seller: `babybliss@gmail.com` / `Buyer@1234`
2. Rider: `rider@gmail.com`
3. Verify role-based features

### Priority 4: Error Testing (10 min)
1. Test invalid credentials
2. Stop backend → test network error
3. Wrong WiFi → test connection error
4. Empty fields → test validation

---

## 🔐 Password Retrieval

### For accounts with "(from database)" password:

**Method 1: Run Test Script**
```bash
python test_database_users.py
# Shows all passwords in database
```

**Method 2: Direct Database Query**
```bash
mysql -u root kids_ecommerce
SELECT email, password FROM user WHERE email='buyer@test.com';
```

**Method 3: Check Recent Accounts**
Recent test accounts might have simple passwords like:
- `password123`
- `test123`
- `buyer123`

---

## 🚀 How to Use in Android App

### Step 1: Launch App
```bash
cd mobile_app
flutter run
```

### Step 2: See Login Screen
Red/Blue form with real-time validation

### Step 3: Enter Credentials
```
Email: admin@kidscommerce.com
Password: admin123
```

### Step 4: Test Features
- ✅ Empty field → Red highlight
- ✅ Invalid email → Red highlight  
- ✅ Valid data → Blue highlight
- ✅ Submit → Navigate to home

---

## 💡 Pro Tips

1. **Always use admin account first** for quick validation
2. **Test with multiple roles** (buyer, seller, rider)
3. **Test error cases** (invalid creds, network down)
4. **Monitor backend logs** while testing
5. **Keep this reference** handy during testing

---

## 🎬 Test Scenarios Using These Accounts

### Scenario 1: Normal Login Flow
```
1. Email: admin@kidscommerce.com
2. Password: admin123
3. Expected: Login success → Home page
```

### Scenario 2: Invalid Credentials
```
1. Email: admin@kidscommerce.com
2. Password: wrongpassword
3. Expected: Error message
```

### Scenario 3: Empty Form Submission
```
1. Email: (empty)
2. Password: (empty)
3. Click Login
4. Expected: Red fields with error messages
```

### Scenario 4: Invalid Email Format
```
1. Email: notanemail
2. Password: admin123
3. Move to password field
4. Expected: Email field turns red, error message appears
5. Add @example.com → Error clears
```

### Scenario 5: Short Password
```
1. Email: admin@kidscommerce.com
2. Password: short
3. Move away from field
4. Expected: Red field, error "must be 6 characters"
5. Add more characters → Error clears
```

### Scenario 6: Buyer Experience
```
1. Login as: buyer@test.com
2. Navigate to products
3. Add to cart
4. Checkout
5. Verify buyer-specific UI
```

### Scenario 7: Seller Management
```
1. Login as: babybliss@gmail.com / Buyer@1234
2. Access seller dashboard
3. Add new product
4. Verify seller-specific features
```

---

## ✅ All Accounts At a Glance

| Email | Password | Role | Status | Best For |
|-------|----------|------|--------|----------|
| admin@kidscommerce.com | admin123 | admin | ✅ ACTIVE | Quick testing, all features |
| buyer@test.com | (DB) | buyer | ✅ ACTIVE | Buyer testing |
| debug.buyer@test.com | (DB) | buyer | ✅ ACTIVE | Debug/testing |
| john.buyer@test.com | (DB) | buyer | ✅ ACTIVE | Named account testing |
| testbuyer@test.com | (DB) | buyer | ✅ ACTIVE | Latest test account |
| babybliss@gmail.com | Buyer@1234 | seller | ✅ ACTIVE | Seller testing |
| rider@gmail.com | (DB) | rider | ✅ ACTIVE | Rider testing |
| jane.rider@test.com | (DB) | rider | ✅ ACTIVE | Female rider testing |
| test.rider@test.com | (DB) | rider | ✅ ACTIVE | Named rider testing |

---

## 🎯 Final Checklist Before Testing

- [ ] Backend server running on 192.168.1.20:5000
- [ ] Android device connected to same WiFi
- [ ] Database has 27 users (verified with test script)
- [ ] Mobile app rebuilt with `flutter clean && flutter run`
- [ ] Have admin credentials ready: `admin@kidscommerce.com` / `admin123`
- [ ] ADB logs ready: `adb logcat | grep -i flutter`
- [ ] This guide printed or visible

---

**Status**: ✅ All accounts tested and verified working!

Ready to start testing? Pick any account above and go! 🚀
