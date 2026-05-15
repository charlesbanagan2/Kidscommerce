# Flutter Setup Guide for Kids Commerce Mobile App

## Prerequisites

Before running the Flutter app, you need to install Flutter SDK on your system.

## Windows Installation Steps

### 1. Install Flutter SDK

1. **Download Flutter SDK:**
   - Go to: https://flutter.dev/docs/get-started/install/windows
   - Download the Flutter SDK zip file
   - Extract it to a location like `C:\flutter`

2. **Add Flutter to PATH:**
   - Open Start Menu and search for "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables..."
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add `C:\flutter\bin`
   - Click OK on all windows

3. **Verify Installation:**
   - Open a new Command Prompt or PowerShell
   - Run: `flutter doctor`

### 2. Install Android Studio

1. **Download Android Studio:**
   - Go to: https://developer.android.com/studio
   - Download and install Android Studio

2. **Install Flutter Plugin:**
   - Open Android Studio
   - Go to File > Settings > Plugins
   - Search for "Flutter" and install it
   - Restart Android Studio

3. **Set up Android Emulator:**
   - Open Android Studio
   - Go to Tools > AVD Manager
   - Click "Create Virtual Device"
   - Select a phone model (e.g., Pixel 6)
   - Select a system image (API 33 or higher)
   - Click Finish and launch the emulator

### 3. Alternative: VS Code Setup

If you prefer VS Code:

1. **Install VS Code:** https://code.visualstudio.com/
2. **Install Flutter Extension:**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Flutter" and install the official Flutter extension
   - Also install "Dart" extension

## Running the Kids Commerce Mobile App

### Step 1: Navigate to Mobile App Directory
```bash
cd mobile_app
```

### Step 2: Install Dependencies
```bash
flutter pub get
```

### Step 3: Check Connected Devices
```bash
flutter devices
```

### Step 4: Run the App
```bash
flutter run
```

### Available Options:
- **Android Emulator:** Make sure Android Studio emulator is running
- **Physical Device:** Enable Developer Options and USB Debugging on your Android phone
- **Web Browser:** `flutter run -d chrome` (for web testing)
- **Windows Desktop:** `flutter run -d windows` (if enabled)

## Troubleshooting

### Flutter Doctor Issues
Run `flutter doctor` to check for issues:
- **Android toolchain:** Install Android Studio and set up emulator
- **Chrome:** Install Google Chrome for web development
- **Visual Studio:** Optional for Windows desktop development

### Common Issues

1. **"flutter command not found":**
   - Restart your command prompt/PowerShell after adding to PATH
   - Verify Flutter installation directory is correct

2. **"No connected devices":**
   - Start Android emulator from Android Studio
   - Connect physical device with USB debugging enabled
   - Run `flutter devices` to see available devices

3. **Gradle build errors:**
   - Run `flutter clean`
   - Run `flutter pub get`
   - Try `flutter run` again

4. **Android license issues:**
   - Run `flutter doctor --android-licenses`
   - Accept all licenses when prompted

## Project Configuration

The mobile app is already configured to connect to your Flask backend:

- **API Base URL:** `http://192.168.100.46:5000/api/v1`
- **Authentication:** JWT tokens with automatic refresh
- **Role-based Navigation:** Buyer vs Rider interfaces

## Development Workflow

1. **Start Backend:**
   ```bash
   cd backend
   python -m flask run --host=0.0.0.0 --port=5000
   ```

2. **Start Mobile App:**
   ```bash
   cd mobile_app
   flutter run
   ```

3. **Test Features:**
   - Registration (Buyer/Rider roles)
   - Login with JWT tokens
   - Role-based navigation
   - API integration

## Next Steps After Setup

Once Flutter is installed and running:

1. **Test Registration:** Create new Buyer and Rider accounts
2. **Test Login:** Verify JWT authentication works
3. **Test Navigation:** Confirm role-based routing
4. **Test API Calls:** Verify backend integration
5. **Develop Features:** Add more functionality to the app

## Additional Resources

- **Flutter Documentation:** https://flutter.dev/docs
- **Flutter YouTube Channel:** https://www.youtube.com/flutter
- **Flutter Community:** https://github.com/flutter/flutter
- **Dart Language:** https://dart.dev/guides

## Quick Start Commands

After Flutter installation:
```bash
# Navigate to project
cd mobile_app

# Get dependencies
flutter pub get

# Check devices
flutter devices

# Run app (select device when prompted)
flutter run

# Or run on specific device
flutter run -d <device_id>
```

Your Kids Commerce mobile app is ready to run once Flutter is installed!
