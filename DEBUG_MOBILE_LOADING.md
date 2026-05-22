# Debug Mobile App Loading Issue

## Problem: Mobile app stuck on loading screen

## Quick Checks:

### 1. Check Flutter Logs
Tingnan ang terminal kung saan nag-run ang `flutter run`. Hanapin:

**API Errors:**
```
❌ Request Error: ApiException: [404] Invalid response from server
❌ Request Error: ApiException: [500] Internal Server Error
❌ Request Error: Connection refused
❌ Request Error: Timeout
```

**Auth Errors:**
```
! Auth requested but no access token available
❌ Token is invalid or expired
❌ Login failed
```

**Network Errors:**
```
SocketException: Failed host lookup
Connection timed out
Connection refused
```

### 2. Check Cloud Backend Status
Open browser: https://kids-kingdom.onrender.com

**Should see:**
- ✅ Website loads
- ✅ Can login
- ✅ Can view products

**If not loading:**
- Backend might be sleeping (Render.com free tier)
- Wait 30-60 seconds for it to wake up
- Refresh page

### 3. Check Mobile App Config
Open: `mobile_app/lib/config/url_config.dart`

**Line 9 should be:**
```dart
static const bool USE_LOCAL = false;  // For cloud
```

**Line 17 should be:**
```dart
static const String _renderUrl = 'https://kids-kingdom.onrender.com';
```

### 4. Common Loading Issues

#### Issue A: Backend is Sleeping (Render.com Free Tier)
**Symptoms:**
- First request takes 30-60 seconds
- Subsequent requests are fast
- Logs show "Connection timeout"

**Solution:**
1. Open https://kids-kingdom.onrender.com in browser
2. Wait for it to load (wakes up the backend)
3. Restart Flutter app
4. Try again

#### Issue B: Wrong URL
**Symptoms:**
- Logs show 404 errors
- "Invalid response from server"

**Solution:**
1. Check `url_config.dart` line 17
2. Should be: `https://kids-kingdom.onrender.com`
3. NOT: `https://kidscommerce-backend.onrender.com`
4. Save and restart app

#### Issue C: No Internet Connection
**Symptoms:**
- "Failed host lookup"
- "Connection refused"

**Solution:**
1. Check phone internet connection
2. Try opening browser on phone
3. Visit https://kids-kingdom.onrender.com
4. If works, restart Flutter app

#### Issue D: Cached Old Config
**Symptoms:**
- Changed config but still using old URL
- Logs show old URL

**Solution:**
```bash
cd mobile_app
flutter clean
flutter pub get
flutter run
```

#### Issue E: Login/Auth Issue
**Symptoms:**
- Stuck on login screen
- "Auth requested but no access token"

**Solution:**
1. Check if you have an account
2. Try registering new account
3. Check backend logs for auth errors

## Step-by-Step Debug Process:

### Step 1: Check Flutter Logs
```bash
# In terminal where flutter run is running
# Look for errors (red text)
# Copy any error messages
```

### Step 2: Wake Up Backend
```bash
# Open in browser
https://kids-kingdom.onrender.com

# Wait for it to load
# Should see homepage
```

### Step 3: Test API Manually
```bash
# In browser or Postman
https://kids-kingdom.onrender.com/api/v1/products

# Should return JSON data or 401 error (OK)
# Should NOT return 404 or connection error
```

### Step 4: Clear Flutter Cache
```bash
cd mobile_app
flutter clean
flutter pub get
flutter run
```

### Step 5: Check Specific Screens

**If stuck on splash screen:**
- Check initialization code
- Check if API calls are timing out

**If stuck on login screen:**
- Try registering new account
- Check auth endpoints

**If stuck after login:**
- Check if products API works
- Check if orders API works

## Quick Fixes:

### Fix 1: Restart Everything
```bash
# Stop Flutter app (Ctrl+C)
# Clear cache
flutter clean
flutter pub get
# Run again
flutter run
```

### Fix 2: Wake Up Backend First
```bash
# Open in browser FIRST
https://kids-kingdom.onrender.com

# Wait 30 seconds
# Then run Flutter app
flutter run
```

### Fix 3: Check URL
```dart
// In url_config.dart
static const bool USE_LOCAL = false;
static const String _renderUrl = 'https://kids-kingdom.onrender.com';
```

### Fix 4: Test Backend
```bash
# In browser
https://kids-kingdom.onrender.com/
https://kids-kingdom.onrender.com/api/v1/products
```

## What to Send Me:

If still not working, send:

1. **Flutter logs** (copy-paste from terminal)
2. **Backend status** (does https://kids-kingdom.onrender.com work in browser?)
3. **Config file** (screenshot of url_config.dart lines 9 and 17)
4. **Where it's stuck** (splash screen? login? after login?)

## Expected Behavior:

### Normal Flow:
1. App starts → Splash screen (2-3 seconds)
2. Login screen appears
3. Enter credentials → Login
4. Home screen with products

### If Backend is Sleeping:
1. App starts → Splash screen
2. Loading... (30-60 seconds) ← Backend waking up
3. Login screen appears
4. Normal flow continues

## Pro Tips:

### Tip 1: Keep Backend Awake
Visit https://kids-kingdom.onrender.com every 10 minutes to keep it awake.

Or use a service like:
- UptimeRobot (free)
- Pingdom
- StatusCake

### Tip 2: Add Timeout Handling
In Flutter app, add timeout to API calls:
```dart
timeout: Duration(seconds: 60)  // For first request
```

### Tip 3: Add Loading Indicator
Show "Waking up server..." message if first request takes >10 seconds.

### Tip 4: Use Local for Development
For faster development, use local backend:
```dart
static const bool USE_LOCAL = true;
```

## Next Steps:

1. ✅ Check Flutter logs for errors
2. ✅ Open https://kids-kingdom.onrender.com in browser
3. ✅ Wait for backend to wake up
4. ✅ Restart Flutter app
5. ✅ Send me the logs if still not working

Good luck! 🚀
