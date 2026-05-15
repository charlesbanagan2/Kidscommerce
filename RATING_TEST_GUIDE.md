# 🧪 Quick Test Guide - Rating System

## 🚀 How to Test

### 1️⃣ Start Backend Server
```bash
cd backend
python app.py
```

### 2️⃣ Start Mobile App
```bash
cd mobile_app
flutter run
```

---

## ✅ Test Scenarios

### Test 1: View Ratings on Product Cards
1. Open mobile app
2. Browse products
3. **Expected:** See star ratings (⭐ 4.5) on each product card
4. **Expected:** See review count next to rating

### Test 2: View Ratings on Product Details
1. Tap any product
2. Scroll to "Ratings & Reviews" section
3. **Expected:** See average rating with stars
4. **Expected:** See total review count
5. **Expected:** See preview of 2 recent reviews

### Test 3: Submit Review (Rating Only)
1. Login as buyer
2. Open a product you purchased
3. Tap "Write Review" button
4. Select 5 stars
5. Tap "Submit Review"
6. **Expected:** Beautiful success animation appears
7. **Expected:** Message: "Salamat sa iyong 5-star review!"
8. **Expected:** Animated stars appear
9. **Expected:** Auto-close after 2 seconds
10. **Expected:** Product rating updates immediately

### Test 4: Submit Review with Images
1. Tap "Write Review"
2. Select 3 stars
3. Add title: "Good product"
4. Add review text: "Works well but could be better"
5. Tap "Add Photo/Video"
6. Select "Choose Photo"
7. Pick 2-3 images
8. **Expected:** Image thumbnails appear
9. Tap "Submit Review"
10. **Expected:** Success animation with 3 stars
11. **Expected:** Review appears with images

### Test 5: Submit Review with Video
1. Tap "Write Review"
2. Select 4 stars
3. Tap "Add Photo/Video"
4. Select "Choose Video"
5. Pick a short video
6. **Expected:** Video icon appears in thumbnail
7. Tap "Submit Review"
8. **Expected:** Success animation
9. **Expected:** Review saved with video

### Test 6: Mixed Media Upload
1. Tap "Write Review"
2. Add 2 images
3. Add 1 video
4. **Expected:** All 3 files show in preview
5. Remove 1 image using X button
6. **Expected:** Only 2 files remain
7. Submit review
8. **Expected:** Success!

### Test 7: Maximum Files Limit
1. Tap "Write Review"
2. Try to add 7 files
3. **Expected:** Error message: "Maximum 6 files allowed"
4. **Expected:** Only 6 files can be added

### Test 8: Public Visibility
1. Submit a review as User A
2. Logout
3. Login as User B
4. View the same product
5. **Expected:** User A's review is visible
6. **Expected:** Rating is updated
7. **Expected:** Review count increased

### Test 9: Empty State
1. View a product with no reviews
2. **Expected:** "No reviews yet" message
3. **Expected:** "Be the first to review" button (if logged in)

### Test 10: Authentication Check
1. Logout
2. View a product
3. **Expected:** No "Write Review" button
4. **Expected:** Only "See All" button visible

---

## 🎯 Success Indicators

### ✅ Visual Checks:
- [ ] Star icons are gold/amber color
- [ ] Rating numbers show 1 decimal (e.g., 4.5)
- [ ] Review count shows in parentheses
- [ ] Success overlay has gradient green check icon
- [ ] Stars animate one by one
- [ ] Tagalog message displays correctly

### ✅ Functional Checks:
- [ ] Can select 1-5 stars
- [ ] Can upload images
- [ ] Can upload videos
- [ ] Can remove uploaded files
- [ ] Submit button works
- [ ] Success animation plays
- [ ] Product refreshes automatically
- [ ] New rating appears immediately
- [ ] All buyers can see reviews

### ✅ Error Handling:
- [ ] Shows error if rating not selected
- [ ] Shows error if file limit exceeded
- [ ] Shows error if network fails
- [ ] Shows error if not authenticated

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to submit review"
**Solution:** Check if user has purchased the product

### Issue: Images not uploading
**Solution:** Check file size and format (JPG, PNG only)

### Issue: Success animation not showing
**Solution:** Check if overlay is being created correctly

### Issue: Rating not updating
**Solution:** Ensure fetchProducts() is called after submission

### Issue: "Maximum 6 files allowed"
**Solution:** This is expected behavior, remove some files

---

## 📊 Expected Results

### After Successful Review:
```
✅ Review saved in database
✅ Media files saved in /static/uploads/reviews/
✅ Product rating recalculated
✅ Review count incremented
✅ Success animation displayed
✅ Product UI refreshed
✅ Review visible to all users
```

### Database Check:
```sql
SELECT * FROM review ORDER BY created_at DESC LIMIT 5;
```

Expected columns:
- id, product_id, user_id, rating, title, content
- media (JSON array)
- verified_purchase (TRUE)
- status ('published')
- created_at (timestamp)

---

## 🎉 Test Complete!

If all tests pass, the rating system is **FULLY WORKING**! 🎊

**Congratulations!** 🎉
- ⭐ Ratings work
- 📸 Media uploads work
- 🎨 Success UI works
- 🌐 Public visibility works
- 📱 Mobile app works

**TAPOS NA ANG TESTING!** ✅
