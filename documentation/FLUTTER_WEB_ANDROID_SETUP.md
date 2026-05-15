# Flutter App - Web & Android Setup Guide

## ✅ Cross-Platform Ready!

The Flutter Kids & Baby Store app is now configured to run on both **Android** and **Web** platforms with a single codebase.

---

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure Flutter is installed
flutter --version

# Web support is enabled by default
# Android support is enabled by default
```

### Install Dependencies
```bash
cd c:\Users\mnban\Documents\kids\mobile_app
flutter pub get
```

---

## 📱 Running on Android

### Option 1: Android Emulator
```bash
# Start Android emulator first
flutter emulators
flutter emulators launch emulator-5554  # or your emulator name

# Run the app
flutter run

# Or specify the target
flutter run -d emulator-5554
```

### Option 2: Physical Android Device
```bash
# Connect device via USB and enable USB debugging
adb devices  # Verify device is connected

# Run the app
flutter run
```

### Build APK
```bash
# Debug APK
flutter build apk

# Release APK (optimized)
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Build for Android Package
```bash
# Play Store bundle
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

---

## 🌐 Running on Web

### Run in Development Mode
```bash
# Chrome (default, best for testing)
flutter run -d chrome

# Firefox
flutter run -d firefox

# Edge
flutter run -d edge

# Safari (macOS only)
flutter run -d safari
```

### Build for Web Production
```bash
# Release build (optimized for production)
flutter build web --release

# Output directory: build/web/
# Contains index.html and all assets
```

### Serve Web App Locally
```bash
# After building
cd build/web
python -m http.server 8000

# Access at: http://localhost:8000
```

### Deploy Web App
The `build/web/` folder can be deployed to:
- Firebase Hosting
- Netlify
- GitHub Pages
- AWS S3
- Any static web hosting service
- Your own web server

---

## 🔧 Platform-Specific Configuration

### API Base URL
The app automatically detects the platform:

```dart
if (kIsWeb) {
  // Web platform
  baseUrl = 'http://192.168.1.20:5000';  
} else {
  // Mobile platforms (Android, iOS)
  baseUrl = 'http://192.168.1.20:5000';
}
```

**For development**, both platforms use: `192.168.1.20:5000`

**For production**, update `lib/services/api_service.dart`:
```dart
// Change baseUrl based on your deployment
static String baseUrl = 'https://your-backend-domain.com';
```

### Platform Detection
Use `kIsWeb` from `package:flutter/foundation.dart`:
```dart
import 'package:flutter/foundation.dart';

if (kIsWeb) {
  // Web-specific code
} else {
  // Mobile-specific code
}
```

---

## 📋 Responsive Design

The app is designed to work on:
- **Mobile**: Portrait (primary), Landscape
- **Tablet**: All orientations
- **Web**: Desktop, tablet, mobile viewport sizes

Layout breakpoints (using MediaQuery):
```dart
// Get screen width
double screenWidth = MediaQuery.of(context).size.width;

// Get screen height  
double screenHeight = MediaQuery.of(context).size.height;

// Check orientation
bool isPortrait = MediaQuery.of(context).orientation == Orientation.portrait;

// Check device type
bool isMobile = screenWidth < 600;
bool isTablet = screenWidth >= 600 && screenWidth < 1200;
bool isDesktop = screenWidth >= 1200;
```

---

## 🌍 Handling Network on Different Platforms

### Android
- Uses device's active network (WiFi or mobile data)
- Network errors caught and displayed to user
- Timeout: 15 seconds (configurable in `ApiService`)

### Web
- Uses browser's network
- CORS headers must be properly configured on backend
- Cross-Origin requests require CORS support

### Backend CORS Configuration (Flask)
```python
# In app.py, ensure CORS is properly configured:
from flask_cors import CORS

CORS(app, resources={r"/api/*": {
    "origins": ["http://192.168.1.20:3000", "http://localhost:3000"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
```

---

## 🗄️ Local Storage (SharedPreferences)

Used for:
- JWT tokens (authentication)
- User session data
- App preferences

**On Android**: SharedPreferences (native)
**On Web**: LocalStorage in browser

Both handled transparently by `shared_preferences` package.

---

## 🐛 Troubleshooting

### Web Build Issues
```bash
# Clean web build
flutter clean
flutter pub get
flutter build web --release

# Clear browser cache
# Ctrl+Shift+Delete in Chrome to open Clear Browsing Data
```

### Android Build Issues
```bash
# Clean Android build
flutter clean
flutter pub get
flutter build apk --release

# If gradle issues:
rm -rf android/.gradle
flutter pub get
flutter build apk --release
```

### Network Connection Issues

**Error**: "Connection refused" or "Cannot reach server"

**Solution**:
1. Verify backend is running: `python app.py`
2. Check backend is accessible:
   - On Android emulator: `adb shell ping 192.168.1.20`
   - On web: Test in browser `http://192.168.1.20:5000/api/products`
3. Verify firewall isn't blocking port 5000
4. For web, ensure backend has CORS enabled

### CORS Errors on Web

**Error**: "Access to XMLHttpRequest blocked by CORS policy"

**Solution**: Update backend CORS configuration and restart Flask server

```python
# In Flask app.py
from flask_cors import CORS
CORS(app)  # Simple: Allow all origins
```

---

## 📊 Build Information

### File Structure
```
mobile_app/
├── android/           # Android-specific code and config
├── web/              # Web-specific code and config
│   ├── index.html    # Web entry point
│   ├── manifest.json # PWA manifest
│   └── icons/        # Web app icons
├── lib/              # Dart code (shared)
│   ├── screens/      # UI screens
│   ├── providers/    # State management
│   ├── services/     # API & services
│   ├── models/       # Data models
│   └── main.dart     # App entry point
├── pubspec.yaml      # Dependencies
└── README.md         # Documentation
```

### Build Sizes (Approximate)
- **Android Debug APK**: 150-200 MB
- **Android Release APK**: 40-50 MB
- **Web Release**: 15-20 MB

---

## ✨ Features Available on Both Platforms

### Buyer Features
- ✅ User registration & login with JWT
- ✅ Browse products (search, filter, sort)
- ✅ View product details
- ✅ Add to cart
- ✅ View shopping cart
- ✅ View order history
- ✅ Track orders
- ✅ View profile

### Rider Features
- ✅ Login with JWT
- ✅ View assigned deliveries
- ✅ Accept/complete deliveries
- ✅ Track earnings
- ✅ Contact customers

---

## 🔐 Security Considerations

### JWT Token Handling
- Tokens stored in SharedPreferences (with encryption on Android)
- On web, stored in browser localStorage
- Include in all API requests via Authorization header

### HTTPS for Production
```dart
// For production, use HTTPS:
static String baseUrl = 'https://your-backend-domain.com';

// Ensure backend certificate is valid
// Handle self-signed certificates only in development
```

### Input Validation
All forms validated before submission:
- Email format validation
- Password strength requirements
- Product quantity limits
- Address validation

---

## 📱 Web App (PWA)

The web app includes PWA (Progressive Web App) features:
- Offline support (with caching)
- Install as app on home screen
- Responsive design
- Fast loading

### Enhance PWA Features
```html
<!-- In web/index.html -->
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#7c3aed">
```

---

## 🚀 Deployment Checklist

### Before Building for Production

#### Web
- [ ] Update API base URL to production domain
- [ ] Enable HTTPS in backend
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile viewport in browser
- [ ] Enable service worker for offline support
- [ ] Configure CDN if using static hosting
- [ ] Test API responses
- [ ] Verify authentication tokens work correctly

#### Android
- [ ] Update API base URL to production domain
- [ ] Enable HTTPS in backend
- [ ] Test on multiple Android versions (API 23+)
- [ ] Test on various screen sizes
- [ ] Verify image loading over HTTPS
- [ ] Test network error handling
- [ ] Generate release keystore
- [ ] Sign APK properly
- [ ] Test on physical devices

### Production Build Commands

```bash
# Web Production
flutter build web --release

# Android Production
flutter build apk --release
flutter build appbundle --release

# Both
flutter build web --release && flutter build apk --release
```

---

## 📞 Testing URLs

### Development
- **Backend API**: http://192.168.1.20:5000
- **Web App (local)**: http://localhost:8000
- **Android Emulator**: Can access 192.168.1.20:5000 directly

### Test Credentials
- **Email**: matt@gmail.com
- **Password**: 030904Jeff!

---

## 📚 Useful Commands

```bash
# Check Flutter devices
flutter devices

# Clean project
flutter clean

# Get dependencies
flutter pub get

# Upgrade dependencies
flutter pub upgrade

# Run tests
flutter test

# Build app
flutter build [platform]  # apk, appbundle, web, windows, macos

# Run with specific device
flutter run -d [device-id]

# Hot reload during development
r     # Hot reload
R     # Hot restart  
q     # Quit
```

---

## ✅ Success Criteria

Your setup is complete when:

1. ✅ `flutter run -d chrome` launches web app
2. ✅ `flutter run -d emulator-5554` launches Android app
3. ✅ Login works on both platforms
4. ✅ Products display correctly
5. ✅ Network calls succeed with proper API responses
6. ✅ No platform-specific build errors
7. ✅ Release builds generate successfully

---

## 🎯 Next Steps

1. **Test Locally**: Run on both web and Android with development backend
2. **Configure Production**: Update API URLs for production
3. **Build Releases**: Generate production builds
4. **Deploy Web**: Upload `build/web/` to hosting service
5. **Submit Android**: Upload APK/AAB to Google Play Store
6. **Monitor**: Track app performance and user feedback

---

## 📖 Additional Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Flutter for Web](https://flutter.dev/multi-platform/web)
- [Flutter for Android](https://flutter.dev/multi-platform/android)
- [Material Design 3](https://m3.material.io/)
- [Flutter Community Packages](https://pub.dev)

---

**🎉 Your Flutter app is now ready for both Android and Web platforms!**
