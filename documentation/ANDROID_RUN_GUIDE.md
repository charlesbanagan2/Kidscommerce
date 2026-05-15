# Run Flutter App on Android - Complete Guide

## 📱 Prerequisites

1. **Android Device or Emulator**
   - USB debugging enabled (if physical device)
   - Same WiFi network as backend server

2. **Backend Running**
   - Flask backend: `192.168.1.20:5000`
   - Status: Verified working ✅

3. **Test Account Ready**
   - Email: `testbuyer@test.com`
   - Password: `test123`
   - Role: Buyer
   - Status: Active ✅

---

## 🔌 Step 1: Connect Android Device

### Physical Device:
```powershell
# Enable USB debugging on phone:
# Settings > Developer Options > USB Debugging (ON)

# Connect via USB cable and run:
adb devices

# Should show: device serial number
```

### Android Emulator:
```powershell
# Open Android Studio > Device Manager
# Launch an emulator (API 21+)
# Wait for boot to complete
```

---

## 🌐 Step 2: Network Configuration

### Verify Network Setup:
```powershell
# Check backend is running
python c:\Users\mnban\Documents\kids\android_debug_guide.py

# Should show:
# ✓ Backend is running (Status: 200)
# ✓ Login API Working!
# Backend URL: http://192.168.1.20:5000
```

### Android Device on Same WiFi:
```
1. Open WiFi Settings on phone
2. Connect to: [Your WiFi Network]
3. Keep phone and PC on SAME network
4. Backend must be accessible from phone
```

### Test Connectivity from Android:
```
Phone browser: http://192.168.1.20:5000/
Should load login page
```

---

## 🚀 Step 3: Run Flutter App

### Option A: Run with USB (Recommended)

```powershell
cd c:\Users\mnban\Documents\kids\mobile_app

# Get dependencies
flutter pub get

# List connected devices
flutter devices

# Run on Android device
flutter run

# Or specify device
flutter run -d <device-id>
```

### Option B: Build APK

```powershell
cd c:\Users\mnban\Documents\kids\mobile_app

# Build release APK
flutter build apk --release

# APK will be at:
# build/app/outputs/flutter-apk/app-release.apk

# Install on device
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Option C: Install from Android Studio

```
1. Open Android Studio
2. Open project: c:\Users\mnban\Documents\kids\mobile_app
3. Connect Android device
4. Click "Run" or press Shift+F10
```

---

## 📝 Step 4: Login on Android

### Launch App:
```
1. Open app on Android device
2. Wait for login screen to load
3. Step 1: Select Role → "Buyer"
4. Step 2: Enter credentials:
   - Email: testbuyer@test.com
   - Password: test123
5. Click Login
```

### Expected Result:
```
✓ Login successful
✓ Redirected to home/dashboard
✓ Phone connected to backend API
```

---

## 🐛 Troubleshooting

### "Connection Error" / "Check Connection"

**Problem:** App says connection failed
**Solution:**
```powershell
# 1. Verify backend is running
python c:\Users\mnban\Documents\kids\quick_test.py

# 2. Test from Android device
# Open browser: http://192.168.1.20:5000/
# Should show login page

# 3. Check IP in app code
# File: lib/services/api_service.dart
# Should have: baseUrl = 'http://192.168.1.20:5000';

# 4. Check firewall
# Windows Firewall Settings
# Allow Python.exe (backend) through firewall
```

### "Emulator can't reach backend"

**Problem:** Using emulator, can't connect to 192.168.1.20
**Solution:**
```
Emulator can reach host machine via: 10.0.2.2
But we use 192.168.1.20 (physical IP) - should work

If using emulator:
1. Verify WiFi on PC is active
2. Try: http://10.0.2.2:5000 (emulator-only)
3. Better: Use physical Android device on WiFi
```

### "APK Installation Failed"

**Problem:** adb install fails
**Solution:**
```powershell
# Clear old app
adb uninstall com.example.kids_commerce

# Try again
adb install build/app/outputs/flutter-apk/app-release.apk

# Or use -r flag to replace
adb install -r build/app/outputs/flutter-apk/app-release.apk
```

### "Invalid Email/Password"

**Problem:** Can't login with testbuyer@test.com / test123
**Solution:**
```powershell
# Verify account exists
python c:\Users\mnban\Documents\kids\check_buyer.py

# If account missing, create it
python c:\Users\mnban\Documents\kids\create_buyer_account.py

# Test backend directly
python c:\Users\mnban\Documents\kids\test_api.py
```

---

## ✅ Verification Checklist

Before running:
- [ ] Backend running at 192.168.1.20:5000
- [ ] Test account created (testbuyer@test.com)
- [ ] Android device connected via USB or WiFi
- [ ] Device has USB debugging enabled
- [ ] Device on same WiFi as backend
- [ ] Flutter dependencies installed (`flutter pub get`)
- [ ] App builds without errors (`flutter analyze`)

---

## 📊 Quick Reference

| Item | Value |
|------|-------|
| Backend URL | `192.168.1.20:5000` |
| Test Email | `testbuyer@test.com` |
| Test Password | `test123` |
| Test Role | `buyer` |
| App Path | `c:\Users\mnban\Documents\kids\mobile_app` |
| API Base | `/api/v1` |

---

## 🔄 Full Command Sequence

```powershell
# Terminal 1: Start backend
cd c:\Users\mnban\Documents\kids
python backend/app.py

# Terminal 2: Run Flutter app
cd c:\Users\mnban\Documents\kids\mobile_app
flutter pub get
flutter run
```

---

## 📱 What to Test on Android

1. **Step 1: Role Selection**
   - ✓ Choose Buyer/Rider
   - ✓ Auto-advance to Step 2

2. **Step 2: Personal Information**
   - ✓ Enter first/last name
   - ✓ Enter email
   - ✓ Phone auto-prefixes with "09"
   - ✓ Password strength bar appears in red
   - ✓ Eye icon toggle shows/hides password
   - ✓ Confirm password field works
   - ✓ Error messages show in red when validation fails

3. **Step 3: Complete Details**
   - ✓ Enter street address
   - ✓ Enter city/province
   - ✓ See buyer/rider specific fields
   - ✓ Complete button works

4. **Login**
   - ✓ testbuyer@test.com / test123
   - ✓ Redirects to home page
   - ✓ API connection successful

---

## 💡 Pro Tips

- Use `flutter run -v` for verbose output (helps debugging)
- Hot reload: Press `r` in terminal after code changes
- Hot restart: Press `R` in terminal to rebuild everything
- View logs: `adb logcat` shows Android system logs
- Check IP: `ipconfig` on PC shows your network IP

