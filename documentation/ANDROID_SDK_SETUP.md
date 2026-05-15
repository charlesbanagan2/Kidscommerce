# Android SDK Setup - ADB Installation

## 🔴 Problem: "ADB not found"

ADB (Android Debug Bridge) comes with Android SDK but it's not in your Windows PATH.

---

## ✅ Solution 1: Find Existing Android SDK

First, check if Android SDK is already installed:

```powershell
# Common installation paths:
C:\Users\mnban\AppData\Local\Android\Sdk
C:\Android\Sdk
D:\Android\Sdk
```

If it exists, add to PATH:

```powershell
# Open Settings
# Search: "Environment Variables"
# Click "Edit the system environment variables"
# Click "Environment Variables..." button
# Under "User variables", click "New..."
  Variable name: ANDROID_HOME
  Variable value: C:\Users\mnban\AppData\Local\Android\Sdk
# Click OK, then add to PATH:
# Edit PATH variable
# Click "New"
# Add: C:\Users\mnban\AppData\Local\Android\Sdk\platform-tools
# Click OK
```

Restart PowerShell and test:
```powershell
adb --version
# Should show: Android Debug Bridge version 1.0.xx
```

---

## ✅ Solution 2: Install Flutter (Includes Android SDK)

If Android SDK not found, install via Flutter:

```powershell
# Download Flutter from:
# https://flutter.dev/docs/get-started/install/windows

# Extract to: C:\flutter
# Add to PATH: C:\flutter\bin

# Run:
flutter doctor

# Follow instructions to install Android SDK
```

---

## ✅ Solution 3: Quick Fix - Run Without ADB Check

If you can't find ADB, just run Flutter directly:

```powershell
cd c:\Users\mnban\Documents\kids\mobile_app

# Connect Android device via USB
# Enable USB Debugging

# Run app
flutter run

# Flutter will auto-detect device
```

---

## 📱 Enable USB Debugging on Android Phone

1. **Go to Settings**
2. **About Phone**
3. **Tap Build Number 7 times** (to enable Developer Options)
4. **Back to Settings**
5. **Developer Options**
6. **Enable USB Debugging**
7. **Allow USB Debugging for this computer** (dialog on phone)

---

## 🔗 Connect USB Cable

```powershell
# Check if phone detected
adb devices

# Should show:
# List of attached devices
# XXXXXXXX    device
```

---

## 🚀 Run Without Backend Commands

Simple way to run:

```powershell
# Terminal 1 - Start Backend
cd c:\Users\mnban\Documents\kids
python backend/app.py

# Terminal 2 - Run Flutter
cd c:\Users\mnban\Documents\kids\mobile_app
flutter run

# Select device when asked
```

---

## 📋 Checklist

- [ ] Android phone connected via USB
- [ ] USB Debugging enabled on phone
- [ ] Allow popup shown on phone screen
- [ ] Backend running (Flask)
- [ ] Flutter installed
- [ ] `adb devices` shows phone (optional)

---

## 🎯 Quick Commands

```powershell
# Test backend
curl http://192.168.1.20:5000/

# List devices
adb devices

# Run Flutter app
flutter run

# Build APK
flutter build apk --release

# Install APK
adb install build/app/outputs/flutter-apk/app-release.apk

# View logs
adb logcat
```

