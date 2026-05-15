# 🚀 RUN NOW - Quick Start Commands

## Choose Your Platform

### 🌐 **RUN ON WEB** (Fastest - Recommended First)

Copy and paste this in PowerShell:

```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter run -d chrome
```

**Then:**
1. Wait for browser to open (may take 10-30 seconds first time)
2. Tap "Browse Products" button to test navigation
3. Test login with: matt@gmail.com / 030904Jeff!
4. While running, press `r` to hot reload after code changes

---

### 📱 **RUN ON ANDROID EMULATOR** 

**Step 1:** Start Android Emulator first
```powershell
# List emulators
flutter emulators

# Start one (replace with your emulator name)
flutter emulators launch Pixel_4_API_30
```

**Step 2:** Run app
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter run
```

**Then:**
1. Wait for app to compile and install
2. Test login with same credentials
3. Verify products load correctly

---

### 📱 **RUN ON PHYSICAL ANDROID DEVICE**

**Step 1:** Connect phone via USB
- Enable USB Debugging in phone settings
- Allow USB connection when prompted

**Step 2:** Verify connection
```powershell
adb devices
# Should show your device
```

**Step 3:** Run app
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter run
```

---

## 🏗️ **BUILD FOR PRODUCTION**

### Web Release Build
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter build web --release

# Output: build/web/
# Ready to deploy to Firebase Hosting, Netlify, etc.
```

### Android Release APK
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter build apk --release

# Output: build\app\outputs\flutter-apk\app-release.apk
```

### Android App Bundle (For Google Play Store)
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter build appbundle --release

# Output: build\app\outputs\bundle\release\app-release.aab
```

---

## 🧹 **If Something Goes Wrong**

### "Cannot connect to backend" Error
```powershell
# Make sure backend is running in Python terminal
# In another terminal window, run:
cd "c:\Users\mnban\Documents\kids"
python app.py
# Keep this running while testing the app
```

### App Won't Start
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter clean
flutter pub get
flutter run -d chrome  # or your target
```

### Web Build Fails
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter clean
flutter pub get
flutter build web --release
```

### Android Build Fails
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter clean
flutter pub get
flutter build apk --release
```

---

## ✅ **TEST CREDENTIALS**

- **Email**: matt@gmail.com
- **Password**: 030904Jeff!

---

## 💡 **Keyboard Shortcuts (While Running)**

- `r` = Hot reload (reload code while running)
- `R` = Hot restart (restart app)
- `q` = Quit app
- `w` = Toggle widget inspector (web)
- `p` = Toggle performance overlay

---

## 📊 **Check if Everything Works**

### Web
```powershell
cd "c:\Users\mnban\Documents\kids\mobile_app"
flutter run -d chrome

# If browser opens: ✅ SUCCESS
```

### Android
```powershell
flutter run

# If app appears on device/emulator: ✅ SUCCESS
```

### Backend
```powershell
cd "c:\Users\mnban\Documents\kids"
python app.py

# If Flask server starts: ✅ SUCCESS
# Should show: "Running on http://192.168.1.20:5000"
```

---

## 🎯 **Complete Setup**

1. **Terminal 1**: Start Flask backend
   ```powershell
   cd "c:\Users\mnban\Documents\kids"
   python app.py
   ```

2. **Terminal 2**: Run Flutter app
   ```powershell
   cd "c:\Users\mnban\Documents\kids\mobile_app"
   flutter run -d chrome
   ```

3. **Test**: Login and browse products in browser

---

## 📁 **File Locations**

- **Flutter App**: `c:\Users\mnban\Documents\kids\mobile_app`
- **Backend**: `c:\Users\mnban\Documents\kids\app.py`
- **Database**: `kids_ecommerce` (MySQL)
- **Web Build Output**: `mobile_app\build\web\`
- **Android Build Output**: `mobile_app\build\app\outputs\`

---

## 🎉 **YOU'RE READY!**

**Pick a platform above and run the command. Your cross-platform app will launch!**

---

## 📞 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | `flutter clean && flutter pub get` |
| "Can't connect to backend" | Run `python app.py` in separate terminal |
| Emulator too slow | Use physical device or Chrome for web |
| Changes not appearing | Press `r` for hot reload |
| Build fails | `flutter clean` then rebuild |

---

**Questions?** Check the full setup guide: `FLUTTER_WEB_ANDROID_SETUP.md`
