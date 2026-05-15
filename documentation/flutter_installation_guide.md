# Flutter and Dart Installation Guide for Windows

## Quick Installation Steps

### Step 1: Download Flutter SDK
1. Go to: https://flutter.dev/docs/get-started/install/windows
2. Download the Flutter SDK zip file
3. Extract it to `C:\flutter`

### Step 2: Add Flutter to PATH
1. Press `Windows + R`, type `sysdm.cpl`, press Enter
2. Click "Advanced" tab > "Environment Variables"
3. Under "System variables", find "Path" and click "Edit"
4. Click "New" and add: `C:\flutter\bin`

### Step 3: Install Android Studio
1. Download from: https://developer.android.com/studio
2. Install Android Studio
3. Open Android Studio > File > Settings > Plugins
4. Search for "Flutter" and install it
5. Restart Android Studio

### Step 4: Set Up Android Emulator
1. Open Android Studio
2. Tools > AVD Manager
3. Click "Create Virtual Device"
4. Choose Pixel 6 or similar
5. Select a system image (API 33 or higher)
6. Finish setup and launch emulator

### Step 5: Verify Installation
Open Command Prompt and run:
```bash
flutter doctor
```

### Step 6: Run Your App
```bash
cd mobile_app
flutter pub get
flutter run
```

---

## Detailed Installation Instructions

### Prerequisites
- Windows 10 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Internet connection

### Step 1: Install Flutter SDK

#### Option A: Manual Installation
1. Download Flutter SDK from https://flutter.dev/docs/get-started/install/windows
2. Create folder `C:\flutter`
3. Extract the downloaded zip file to `C:\flutter`
4. Add `C:\flutter\bin` to your PATH environment variable

#### Option B: Using PowerShell (Automated)
```powershell
# Create Flutter directory
New-Item -ItemType Directory -Path "C:\flutter" -Force

# Download Flutter (run as Administrator)
Invoke-WebRequest -Uri "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.19.6-stable.zip" -OutFile "C:\flutter.zip"

# Extract Flutter
Expand-Archive -Path "C:\flutter.zip" -Destination "C:\" -Force

# Clean up
Remove-Item "C:\flutter.zip"

# Add to PATH (run as Administrator)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\flutter\bin", "Machine")
```

### Step 2: Verify Flutter Installation
Open a NEW Command Prompt and run:
```bash
flutter --version
```

### Step 3: Run Flutter Doctor
```bash
flutter doctor
```

This will show what components are installed and what's missing.

### Step 4: Install Missing Components

#### Android Studio Setup
1. Download Android Studio from https://developer.android.com/studio
2. Install with default settings
3. Launch Android Studio
4. Install Flutter plugin:
   - File > Settings > Plugins
   - Search "Flutter" and install
   - Restart Android Studio

#### Android SDK Setup
1. In Android Studio: Tools > SDK Manager
2. Install Android SDK Platform-Tools
3. Install a system image (API 33 or higher)

#### Create Android Virtual Device
1. Tools > AVD Manager
2. Create Virtual Device
3. Choose hardware (Pixel 6 recommended)
4. Select system image
5. Finish and launch

### Step 5: Accept Android Licenses
```bash
flutter doctor --android-licenses
```
Type 'y' and accept all licenses.

### Step 6: Test Flutter Installation
```bash
flutter doctor
```

All items should have checkmarks now.

### Step 7: Run Your Kids Commerce App
```bash
cd mobile_app
flutter pub get
flutter run
```

## Troubleshooting

### Common Issues

#### "flutter command not found"
- Restart Command Prompt after adding to PATH
- Verify PATH includes `C:\flutter\bin`

#### "Android toolchain not installed"
- Install Android Studio
- Install Flutter plugin
- Accept Android licenses

#### "Connected device" issues
- Start Android emulator from Android Studio
- Or connect physical Android device with USB debugging

#### "Unable to locate adb"
- Add Android SDK platform-tools to PATH
- Usually at: `C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools`

### Performance Tips
- Use SSD for better performance
- Allocate more RAM to Android emulator
- Use physical device for better testing

## Alternative: Web Development
If you prefer web development without Android setup:
```bash
cd mobile_app
flutter pub get
flutter run -d chrome
```

## Next Steps
1. Start the Flask backend: `cd backend && python -m flask run --host=0.0.0.0 --port=5000`
2. Run the Flutter app: `cd mobile_app && flutter run`
3. Test the complete e-commerce functionality!

## Support
- Flutter documentation: https://flutter.dev/docs
- Flutter issues: https://github.com/flutter/flutter/issues
- Stack Overflow: Use [flutter] tag

Your Kids Commerce Flutter app is ready to run once Flutter is installed!
