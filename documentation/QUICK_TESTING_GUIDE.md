# Quick Testing Guide - Images & Store Navigation ✅

## Setup Required

1. **Backend running:**
   ```bash
   cd c:\Users\mnban\Documents\kids\backend
   python app.py
   ```
   Should show: `Running on http://192.168.1.20:5000` (or your local IP)

2. **Mobile app ready:**
   ```bash
   cd c:\Users\mnban\Documents\kids\mobile_app
   flutter run
   ```

3. **Website (optional):**
   - Access at: `http://localhost:5000`

## 5-Minute Quick Test

### Step 1: Check Hero Images (1 min)
1. Open mobile app
2. **Look at carousel at TOP of home screen**
3. Should see 4 rotating images
4. Images should NOT be broken/placeholder icons

**✅ Pass** = See real images  
**❌ Fail** = See gray boxes with image icons

---

### Step 2: Check Product Images (1 min)
1. Scroll down to "Daily Discover" section
2. **Look at product grid cards**
3. Each card should show main product image
4. Images should NOT be placeholder/broken

**✅ Pass** = Product images display  
**❌ Fail** = Gray boxes or missing images

---

### Step 3: Check Real-Time Badge Removed (1 min)
1. Look at "Daily Discover" header
2. **Should only see: "Daily Discover" text**
3. NO blue/green indicators
4. NO "Updating" or "Real-time" text
5. NO spinner icon

**✅ Pass** = Clean header  
**❌ Fail** = See badge or indicator

---

### Step 4: View Shop Button - Mobile (1 min)
1. Tap any product in grid
2. On product detail page, find store section
3. **Click "View Shop" button**
4. Should navigate to store page

**✅ Pass** = See store page with all seller's products  
**❌ Fail** = Nothing happens or error

---

### Step 5: Visit Store Button - Website (1 min)
1. Go to `http://localhost:5000`
2. Click any product
3. In store section, **click "Visit Store"**
4. Should navigate to `/store/<seller_id>`

**✅ Pass** = See store page  
**❌ Fail** = Nothing happens or error

---

## Detailed Testing

### Mobile App Store Page Test
**If Quick Test Step 4 passed:**

1. On store detail screen, you should see:
   - Store logo (circular) at top ✅
   - Store name ✅
   - "X products" count ✅
   - Search box ✅
   - Grid of all seller's products ✅

2. Try searching:
   - Type product name in search box
   - Results should filter ✅
   - Can see matching products ✅

3. Click on a product from store:
   - Should open product detail screen ✅
   - Should show correct product info ✅

---

### Website Store Page Test
**If Quick Test Step 5 passed:**

1. On store page (`/store/<id>`), you should see:
   - Store header information ✅
   - Store logo ✅
   - All seller's products ✅
   - Product listing ✅

2. Click on product:
   - Should open product detail ✅
   - Should show correct info ✅

---

## Troubleshooting

### Problem: Images Still Show as Broken/Gray Boxes

**Check 1: Backend IP Address**
```bash
# In PowerShell, find your machine's IP
ipconfig

# Look for IPv4 Address (typically 192.168.x.x)
# Should match the hardcoded IP in Flutter code
```

**Check 2: Verify Backend Images Exist**
```bash
# Check if upload folder has images
dir "c:\Users\mnban\Documents\kids\backend\app\static\uploads\"

# Should show files like:
# hero_slide_1.png
# Make_this_Christmas_merry_and_bright...
# etc.
```

**Check 3: Verify Image URLs Work**
```bash
# Open in browser:
http://192.168.1.20:5000/static/uploads/hero_slide_1.png

# Should download or display the image
# If 404 error, images don't exist in backend
```

**Check 4: Update IP if Needed**
If your backend IP is NOT `192.168.1.20`:

Edit `mobile_app/lib/screens/buyer_app/buyer_home_screen.dart`:
```dart
// Change all URLs to use your actual IP
_heroSlides = [
  'http://YOUR_IP:5000/static/uploads/hero_slide_1.png',
  // ... etc
];
```

Then rebuild: `flutter run`

---

### Problem: Store Page Shows No Products

**Check 1: Does Seller Have Products?**
```bash
# In backend, search seller in database:
mysql -u root kids_ecommerce
SELECT id, name, seller_id FROM product WHERE seller_id = X;
```

**Check 2: Are Products Active?**
```bash
# Products must have status='active'
SELECT id, name, status FROM product WHERE seller_id = X;

# If status is 'draft', they won't show
```

**Check 3: Is Seller Registered?**
- Seller must have SellerApplication entry
- Status must be 'approved'

---

### Problem: "View Shop" Button Not Working

**Check 1: Correct Import?**
```dart
// product_detail_screen.dart should have:
import 'store_detail_screen.dart';
```

**Check 2: Product Has Seller Info?**
```dart
// In app, check console:
print('Seller ID: ${widget.product.sellerId}');
print('Store Name: ${widget.product.storeName}');

// Should not be null or 0
```

---

## Console Output to Look For

### Mobile App (Good Signs)
```
✅ Auto-refreshing products...  (means sync still works)
✅ Found X updated/new products  (means updates working)
✅ Product sync complete  (means background refresh works)
```

### Mobile App (Bad Signs)
```
❌ Image load failed
❌ NetworkImageLoadException
❌ Exception: 404
```
If you see these, images aren't loading - check IP address

---

## File Changes Summary

### Files Changed (3 files)
1. `mobile_app/lib/screens/buyer_app/buyer_home_screen.dart`
   - Hero URL: 127.0.0.1 → 192.168.1.20
   - Removed real-time badge UI

2. `mobile_app/lib/screens/buyer_app/product_detail_screen.dart`
   - Placeholder URL: 127.0.0.1 → 192.168.1.20
   - "View Shop" button now navigates to StoreDetailScreen
   - Added import: `store_detail_screen.dart`

3. `mobile_app/lib/screens/buyer_app/store_detail_screen.dart` ✨ NEW
   - Complete store page showing all seller's products
   - Search functionality
   - Product grid with clickable items

### Files NOT Changed
- Website files (already working)
- Backend API (already correct)
- Backend database (no schema changes)

---

## Quick Commands Reference

```bash
# Build and run mobile app
cd mobile_app
flutter clean
flutter pub get
flutter run

# Check for errors
flutter analyze

# View live logs
flutter logs

# Rebuild website if needed (usually not necessary)
cd backend
python app.py  # Restart Flask

# Database check (if needed)
mysql -u root
USE kids_ecommerce;
SELECT * FROM product LIMIT 5;
```

---

## Expected Results

### ✅ Success Looks Like:
- Hero carousel rotating smoothly with product images
- Product grid showing product photos
- "Daily Discover" header (clean, no badge)
- Click "View Shop" → Store page loads
- Store page shows 2-column grid of products
- Can search products in store
- Click product → Product detail page opens
- Website "Visit Store" works too

### ❌ Failure Looks Like:
- Gray boxes with image icons (broken images)
- "Real-time" or "Updating" badge on home screen
- "View Shop" button does nothing
- Store page shows "No products available"
- Any error messages in console

---

## Support Steps

If something doesn't work:

1. **Check backend is running:**
   ```bash
   curl http://192.168.1.20:5000/api/v1/products
   # Should return JSON array of products
   ```

2. **Check images exist:**
   ```bash
   ls -la backend/app/static/uploads/
   # Should show hero_slide_1.png and other images
   ```

3. **Check IP address:**
   ```bash
   ipconfig getifaddr en0  # Mac/Linux
   # or use ipconfig on Windows
   ```

4. **Rebuild app:**
   ```bash
   cd mobile_app
   flutter clean
   flutter pub get
   flutter run
   ```

5. **Check Flutter analyzer:**
   ```bash
   flutter analyze
   # Should show "No issues found"
   ```

---

## Timeline: How Long Each Test Takes

- Quick Test: **5 minutes** (all 5 steps)
- Detailed Test: **10 minutes**
- Full Verification: **15 minutes**

Choose based on how thorough you want to be!

