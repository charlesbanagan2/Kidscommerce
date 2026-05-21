# Wishlist Persistence Test Plan

## ✅ Backend Verification

### Database Structure
```python
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ✅ Links to user
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ✅ Links to product
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Timestamp
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product')
```

**✅ Persistence Confirmed:**
- Data is stored in database table `wishlist`
- Linked to `user_id` - survives logout
- Linked to `product_id` - maintains product reference
- Has `created_at` timestamp

### API Endpoints

#### 1. GET /api/v1/wishlist
**Purpose:** Retrieve user's wishlist
**Authentication:** Required (`@token_required`)
**Query:** Joins `Wishlist` and `Product` tables filtered by `user_id`
**Response:**
```json
{
  "success": true,
  "wishlist_items": [
    {
      "id": 1,
      "product_id": 123,
      "product_name": "Product Name",
      "product_image": "/static/uploads/image.jpg",
      "price": 99.99,
      "stock": 10,
      "added_at": "2025-01-01T12:00:00"
    }
  ]
}
```
**✅ Persistence:** Reads from database, returns all saved items for user

#### 2. POST /api/v1/wishlist
**Purpose:** Add product to wishlist
**Authentication:** Required (`@token_required`)
**Request Body:**
```json
{
  "product_id": 123
}
```
**Database Action:**
```python
new_wishlist_item = Wishlist(
    user_id=request.current_user_id,  # ✅ Saves with user ID
    product_id=product_id
)
db.session.add(new_wishlist_item)
db.session.commit()  # ✅ Commits to database
```
**✅ Persistence:** Writes to database, survives logout

#### 3. DELETE /api/v1/wishlist?product_id=123
**Purpose:** Remove product from wishlist
**Authentication:** Required (`@token_required`)
**Database Action:**
```python
wishlist_item = Wishlist.query.filter_by(
    user_id=request.current_user_id,
    product_id=product_id
).first()
db.session.delete(wishlist_item)
db.session.commit()  # ✅ Commits deletion to database
```
**✅ Persistence:** Deletes from database permanently

---

## 🧪 Manual Test Procedure

### Test 1: Add Products to Wishlist
**Steps:**
1. ✅ Open mobile app
2. ✅ Login with test account (e.g., buyer@test.com)
3. ✅ Navigate to product detail screen
4. ✅ Tap heart icon on 3 different products
5. ✅ Verify heart icon turns red/filled
6. ✅ Verify "Added to liked products" message appears
7. ✅ Navigate to Profile → Wishlist
8. ✅ Verify all 3 products appear in wishlist

**Expected Result:** ✅ All 3 products saved to wishlist

---

### Test 2: Logout and Login - Verify Persistence
**Steps:**
1. ✅ From Profile screen, tap "Sign Out"
2. ✅ Confirm logout
3. ✅ Verify redirected to login screen
4. ✅ Login again with same account (buyer@test.com)
5. ✅ Navigate to Profile → Wishlist
6. ✅ Verify all 3 products still appear in wishlist
7. ✅ Navigate to product detail of a liked product
8. ✅ Verify heart icon is still red/filled

**Expected Result:** ✅ All wishlist data persists after logout/login

---

### Test 3: Remove from Wishlist
**Steps:**
1. ✅ Navigate to Profile → Wishlist
2. ✅ Tap heart icon on one product to remove
3. ✅ Verify "Removed from wishlist" message appears
4. ✅ Verify product disappears from wishlist
5. ✅ Verify wishlist count decreases (e.g., 3 → 2)
6. ✅ Navigate to that product's detail screen
7. ✅ Verify heart icon is now outlined (not filled)

**Expected Result:** ✅ Product removed from wishlist

---

### Test 4: Logout and Login - Verify Removal Persists
**Steps:**
1. ✅ Logout from app
2. ✅ Login again with same account
3. ✅ Navigate to Profile → Wishlist
4. ✅ Verify only 2 products remain (removed product not there)
5. ✅ Navigate to removed product's detail screen
6. ✅ Verify heart icon is still outlined (not filled)

**Expected Result:** ✅ Removal persists after logout/login

---

### Test 5: Multiple Sessions - Different Devices
**Steps:**
1. ✅ Login on Device A (or browser)
2. ✅ Add Product X to wishlist
3. ✅ Logout from Device A
4. ✅ Login on Device B (or different browser) with same account
5. ✅ Navigate to wishlist
6. ✅ Verify Product X appears in wishlist

**Expected Result:** ✅ Wishlist syncs across devices/sessions

---

### Test 6: Different Users - Isolated Wishlists
**Steps:**
1. ✅ Login as User A (buyer@test.com)
2. ✅ Add Product 1, 2, 3 to wishlist
3. ✅ Logout
4. ✅ Login as User B (buyer2@test.com)
5. ✅ Verify wishlist is empty (or has different products)
6. ✅ Add Product 4, 5 to wishlist
7. ✅ Logout
8. ✅ Login as User A again
9. ✅ Verify wishlist still shows Product 1, 2, 3 (not 4, 5)

**Expected Result:** ✅ Each user has isolated wishlist data

---

## 🔍 Database Verification (Optional)

### Check Database Directly
```sql
-- View all wishlist entries
SELECT w.id, w.user_id, w.product_id, w.created_at, 
       u.email, p.name as product_name
FROM wishlist w
JOIN user u ON w.user_id = u.id
JOIN product p ON w.product_id = p.id
ORDER BY w.created_at DESC;

-- Check specific user's wishlist
SELECT w.id, w.product_id, p.name, w.created_at
FROM wishlist w
JOIN product p ON w.product_id = p.id
WHERE w.user_id = 1;  -- Replace with actual user_id

-- Count wishlist items per user
SELECT u.email, COUNT(w.id) as wishlist_count
FROM user u
LEFT JOIN wishlist w ON u.id = w.user_id
GROUP BY u.id, u.email;
```

---

## 📊 Test Results Template

### Test Execution Date: _____________

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Add Products to Wishlist | ⬜ Pass / ⬜ Fail | |
| 2 | Logout/Login Persistence | ⬜ Pass / ⬜ Fail | |
| 3 | Remove from Wishlist | ⬜ Pass / ⬜ Fail | |
| 4 | Removal Persistence | ⬜ Pass / ⬜ Fail | |
| 5 | Multiple Sessions | ⬜ Pass / ⬜ Fail | |
| 6 | Isolated User Wishlists | ⬜ Pass / ⬜ Fail | |

### Issues Found:
```
[List any issues discovered during testing]
```

### Screenshots:
```
[Attach screenshots of key test steps]
```

---

## 🐛 Troubleshooting

### Issue: Wishlist empty after login
**Possible Causes:**
1. Token not properly stored/retrieved
2. User ID mismatch
3. Database query filtering wrong user

**Debug Steps:**
```dart
// In buyer_provider.dart fetchWishlist()
debugPrint('🔍 Fetching wishlist for user: ${request.current_user_id}');
debugPrint('🔍 Wishlist data received: $wishlistData');
```

### Issue: Heart icon not showing correct state
**Possible Causes:**
1. `_wishlistProductIds` not populated
2. `isProductLiked()` not called correctly
3. Provider not notifying listeners

**Debug Steps:**
```dart
// In product_detail_screen.dart
debugPrint('🔍 Product ID: ${widget.product.id}');
debugPrint('🔍 Is Liked: ${buyerProvider.isProductLiked(widget.product.id)}');
debugPrint('🔍 Wishlist IDs: ${buyerProvider.wishlistProductIds}');
```

### Issue: Changes not persisting
**Possible Causes:**
1. Database commit not called
2. Transaction rolled back
3. Database connection issue

**Debug Steps:**
```python
# In app.py api_v1_wishlist()
app.logger.info(f"Adding to wishlist: user_id={request.current_user_id}, product_id={product_id}")
db.session.commit()
app.logger.info("Wishlist item committed to database")
```

---

## ✅ Expected Behavior Summary

1. **Persistence:** Wishlist data is stored in database and survives logout/login
2. **Sync:** Wishlist syncs across all screens (Product Detail, Wishlist, Profile)
3. **Real-time:** Changes reflect immediately in UI via Provider
4. **Isolation:** Each user has their own wishlist data
5. **Consistency:** Heart icon state matches database state
6. **Messages:** Correct messages shown for add/remove actions

---

## 🚀 Ready to Test!

Follow the test procedures above and mark each test as Pass/Fail. If any test fails, use the troubleshooting section to debug the issue.
