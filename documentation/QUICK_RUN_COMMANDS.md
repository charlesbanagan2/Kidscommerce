# Quick Commands - Run App on Web & Android

## 🚀 Run on Web (Recommended for Quick Testing)

```bash
cd c:\Users\mnban\Documents\kids\mobile_app

# Run on Chrome (fastest)
flutter run -d chrome

# Or Firefox
flutter run -d firefox
```

Then open browser at `http://localhost:xxxxx` (shown in terminal)

---

## 📱 Run on Android Emulator

```bash
cd c:\Users\mnban\Documents\kids\mobile_app

# List available emulators
flutter emulators

# Launch emulator (replace with your emulator name)
flutter emulators launch Pixel_4_API_30

# Run app on emulator
flutter run
```

---

## 📱 Run on Physical Android Device

```bash
# Connect via USB, enable USB debugging

# Verify device connected
adb devices

# Run app
cd c:\Users\mnban\Documents\kids\mobile_app
flutter run
```

---

## 🔨 Build for Production

### Web Release
```bash
cd c:\Users\mnban\Documents\kids\mobile_app
flutter build web --release
# Output: build/web/
```

### Android APK Release
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (for Google Play)
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

---

## ✨ Hot Reload During Development

While app is running:
- Press `r` to hot reload code changes
- Press `R` for hot restart
- Press `q` to quit

---

## 🧹 Clean & Rebuild

```bash
flutter clean
flutter pub get
flutter run -d chrome  # or your target
```

---

## 📊 Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart              # App entry point
│   ├── screens/               # UI screens (shared)
│   ├── providers/             # State management
│   ├── services/api_service.dart  # API calls
│   └── models/                # Data models
├── web/                       # Web-specific (index.html, manifest.json)
├── android/                   # Android-specific (gradle, manifests)
├── pubspec.yaml              # Dependencies
└── README.md
```

---

## 🌐 API Base URL

Currently set to: `http://192.168.1.20:5000`

**To change for production**, edit:
```
lib/services/api_service.dart
```

Find this line:
```dart
static String baseUrl = 'http://192.168.1.20:5000';
```

Change to your production URL:
```dart
static String baseUrl = 'https://your-domain.com';
```

---

## ✅ Test Login

- **Email**: matt@gmail.com
- **Password**: 030904Jeff!

---

## 🚨 Common Issues & Fixes

### Web won't start
```bash
flutter clean
flutter pub get
flutter run -d chrome
```

### Android emulator is slow
Use a faster emulator or physical device:
```bash
flutter run -d [physical-device-id]
```

### "Cannot connect to server" error
```bash
# Check backend is running
python c:\Users\mnban\Documents\kids\app.py

# On Android emulator, verify it can reach backend
adb shell ping 192.168.1.20
```

### Build fails
```bash
flutter clean
flutter pub get
flutter analyze  # Check for errors
```

---

## 📱 Available Platforms

✅ Web (Chrome, Firefox, Safari, Edge)
✅ Android (API 23+)
⏳ iOS (iOS 11+) - Currently requires macOS

---

**Ready to run! Pick your platform and go!** 🎉
