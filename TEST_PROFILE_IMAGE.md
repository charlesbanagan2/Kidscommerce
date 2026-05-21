# Profile Image Persistence - Test Guide

## Test Scenario 1: Buyer Profile Image Persistence

### Steps:
1. **Login as Buyer**
   - Open the mobile app
   - Login using buyer credentials

2. **Upload Profile Image**
   - Go to Profile screen
   - Tap Edit Profile
   - Tap camera icon to upload profile image
   - Select an image from gallery
   - Wait for upload to complete
   - Verify image appears in edit screen
   - Tap "Save Changes"

3. **Verify Image Displays**
   - Go back to Profile screen
   - ✅ Profile image should display correctly

4. **Test Persistence After Logout**
   - Logout from the app
   - Login again using same buyer credentials
   - Go to Profile screen
   - ✅ Profile image should still display correctly

5. **Test Persistence After App Restart**
   - Close the app completely
   - Open the app again
   - Login using same buyer credentials
   - Go to Profile screen
   - ✅ Profile image should still display correctly

---

## Test Scenario 2: Rider Profile Image Persistence

### Steps:
1. **Login as Rider**
   - Open the mobile app
   - Login using rider credentials

2. **Upload Profile Image**
   - Go to Profile screen (rider profile)
   - Tap Edit Profile
   - Tap camera icon to upload profile image
   - Select an image from gallery
   - Wait for upload to complete
   - Verify image appears in edit screen
   - Tap "Save Changes"

3. **Verify Image Displays**
   - Go back to Profile screen
   - ✅ Profile image should display correctly

4. **Test Persistence After Logout**
   - Logout from the app
   - Login again using same rider credentials
   - Go to Profile screen
   - ✅ Profile image should still display correctly

5. **Test Persistence After App Restart**
   - Close the app completely
   - Open the app again
   - Login using same rider credentials
   - Go to Profile screen
   - ✅ Profile image should still display correctly

---

## Test Scenario 3: Multiple Login/Logout Cycles

### Steps:
1. Login as Buyer with profile image
2. Verify image displays
3. Logout
4. Login as Rider with profile image
5. Verify image displays
6. Logout
7. Login as Buyer again
8. ✅ Buyer profile image should still display
9. Logout
10. Login as Rider again
11. ✅ Rider profile image should still display

---

## Expected Results

### ✅ Success Criteria:
- Profile image displays immediately after upload
- Profile image persists after logout and login
- Profile image persists after app restart
- No loading delays or flickering
- No errors in console logs
- Image quality is maintained

### ❌ Failure Indicators:
- Profile image disappears after logout
- Profile image shows placeholder/initial after login
- Image takes too long to load
- Errors in console about image loading
- Image quality is degraded

---

## Debug Commands

If issues occur, check these:

### 1. Check Flutter Logs
```bash
flutter logs
```

### 2. Check for Errors
Look for these in logs:
- "Failed to refresh user profile"
- "Error loading stored data"
- "Failed to upload photo"

### 3. Check Network Requests
- Verify `/api/v1/user/profile` endpoint is called
- Verify profile image URL is returned in response
- Check if image URL is valid and accessible

### 4. Check SharedPreferences
The user data should be saved with profile_image field:
```json
{
  "id": "...",
  "email": "...",
  "full_name": "...",
  "profile_image": "/uploads/profile_photos/...",
  "role": "buyer"
}
```

---

## Troubleshooting

### Issue: Image doesn't display after login
**Solution**: 
- Check if `refreshUser()` is being called in profile screen
- Verify backend returns profile_image in user profile response
- Check console logs for errors

### Issue: Image displays but disappears after logout
**Solution**:
- This should be fixed now
- Verify the fix is applied to both profile screens
- Check if SharedPreferences is saving user data correctly

### Issue: Image loads slowly
**Solution**:
- This is expected on first load (fetching from backend)
- Subsequent loads should be faster (cached in SharedPreferences)
- Consider adding loading indicator if needed

---

## Notes

- Profile images are stored in backend: `/uploads/profile_photos/`
- Images are served through `UrlConfig.toAbsoluteImageUrl()`
- User data is cached in SharedPreferences
- Profile data is refreshed from backend on profile screen load
- Changes are automatically reflected through Provider pattern

---

**Test Date**: _____________
**Tested By**: _____________
**Result**: ☐ PASS  ☐ FAIL
**Notes**: _____________________________________________
