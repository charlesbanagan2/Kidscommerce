# Test Google Login - Quick Guide

## What Was Fixed
The Google login token persistence issue has been fixed. Tokens are now saved to storage BEFORE being used, preventing "Token is missing" errors.

## How to Test

### 1. Clean Test (Recommended)
```bash
# Clear app data to start fresh
adb shell pm clear com.example.mobile_app

# Or uninstall and reinstall
flutter clean
flutter pub get
flutter run
```

### 2. Test Google Login
1. Open the app
2. Click "Sign in with Google" button
3. Select your Google account
4. Complete the authentication

### 3. What to Look For

#### ✅ SUCCESS - You should see:
```
=== GOOGLE LOGIN RESPONSE ===
✅ Tokens created from nested format (Google)
✅ User created: [Your Name], Role: buyer, Authenticated: true
✅ Tokens set in ApiService after saving to storage
=== GOOGLE LOGIN COMPLETE ===
```

Then immediately after:
```
🔤 API GET http://192.168.1.26:5000/api/v1/notifications/unread-count
🔑 Using access token: eyJhbGciOiJIUzI1NiIs...
🔥 API Response (200): {"unread_count": 0, "success": true}
```

#### ❌ FAILURE - You would see (but shouldn't anymore):
```
🔤 API GET http://192.168.1.26:5000/api/v1/notifications/unread-count
! Auth requested but no access token available
🔥 API Response (401): {"message": "Token is missing", "success": false}
```

### 4. Verify Persistence
1. After successful login, close the app completely
2. Reopen the app
3. You should remain logged in
4. API calls should work immediately

### 5. Check Logs
Use Android Studio or VS Code to monitor the logs:
```bash
# Or use adb logcat
adb logcat | grep -E "flutter|API|Token|Auth"
```

## Expected Behavior

### Login Flow:
1. ✅ User clicks Google sign-in
2. ✅ Google authentication completes
3. ✅ Backend returns tokens
4. ✅ Tokens saved to SharedPreferences
5. ✅ Tokens set in ApiService
6. ✅ User navigates to home screen
7. ✅ API calls work with saved tokens

### After App Restart:
1. ✅ App loads
2. ✅ AuthProvider initializes
3. ✅ Tokens loaded from SharedPreferences
4. ✅ Tokens set in ApiService
5. ✅ User remains logged in
6. ✅ API calls work immediately

## Troubleshooting

### If login still fails:

1. **Check backend is running**
   ```bash
   curl http://192.168.1.26:5000/api/health
   ```

2. **Check Google OAuth configuration**
   - Verify `google_oauth_config.dart` has correct client IDs
   - Check backend has Google OAuth enabled

3. **Clear app data and retry**
   ```bash
   adb shell pm clear com.example.mobile_app
   ```

4. **Check backend logs**
   - Look for `/api/v1/auth/google-login` endpoint
   - Verify it returns tokens in the response

### Common Issues:

**Issue**: "Token is missing" after login
**Solution**: This should be fixed now. If it still happens, check that the fix was applied correctly.

**Issue**: Google sign-in cancelled
**Solution**: User cancelled the sign-in. This is normal behavior.

**Issue**: "This account is not authorized"
**Solution**: The account role is not 'buyer' or 'rider'. Only these roles can use the mobile app.

## Backend Verification

The backend should return tokens in this format:
```json
{
  "success": true,
  "tokens": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "expires_in": 86400
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "buyer"
  }
}
```

Or the old flat format:
```json
{
  "success": true,
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "buyer"
  }
}
```

Both formats are now supported.

---
**Status**: Ready to test ✅  
**Priority**: HIGH - Core authentication feature
