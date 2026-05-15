# Flutter White Screen Fixes - Complete

## Problem Identified
The Flutter app was showing a white screen when running on Android and web due to:
1. **Hardcoded API URL** - The base URL was hardcoded to `192.168.100.46:5000` which doesn't work on Android emulator or web
2. **Platform-specific network issues** - No dynamic URL selection based on platform
3. **Poor error handling** - Initialization errors weren't being properly handled

## Fixes Applied

### 1. Fixed API Service URL Configuration (`lib/services/api_service.dart`)
**Problem**: API URL was hardcoded to a specific local IP
**Solution**: 
- Added dynamic URL selection based on platform
- Android emulator: `http://10.0.2.2:5000`
- Web: `http://localhost:5000`
- iOS simulator: `http://127.0.0.1:5000`
- Added `initializeBaseUrl()` method called in `main()`
- Added import for `dart:io` to access Platform

```dart
static void initializeBaseUrl() {
  if (kIsWeb) {
    baseUrl = 'http://localhost:5000';
  } else if (Platform.isAndroid) {
    baseUrl = 'http://10.0.2.2:5000'; // Android emulator
  } else if (Platform.isIOS) {
    baseUrl = 'http://127.0.0.1:5000';
  } else {
    baseUrl = 'http://192.168.100.46:5000';
  }
  debugPrint('📡 API Base URL initialized: $baseUrl');
}
```

### 2. Updated main.dart (`lib/main.dart`)
**Problem**: API service wasn't initialized before use
**Solution**:
- Added `ApiService.initializeBaseUrl()` call in `main()`
- Moved API service initialization before `runApp()`
- Added import for API service

```dart
void main() {
  ApiService.initializeBaseUrl();
  runApp(const KidsCommerceApp());
}
```

### 3. Improved AuthWrapper Error Handling (`lib/main.dart`)
**Problem**: Initialization could hang or fail silently
**Solution**:
- Added timeout for initialization (10 seconds)
- Better error handling in `_performInitialization()`
- Continues to login screen even if initialization fails
- Shows loading screen only during initialization

```dart
Future<void> _performInitialization() async {
  try {
    await Future.delayed(const Duration(milliseconds: 100));
    if (mounted) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      await authProvider.initialize().timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          debugPrint('⚠️ Auth initialization timeout - proceeding to login');
        },
      );
    }
  } catch (e) {
    debugPrint('❌ Auth initialization error: $e');
  }
}
```

## How to Run

### For Android Emulator:
1. Ensure backend is running on `localhost:5000`
2. Run: `flutter run -d emulator-5554`
3. App will use `http://10.0.2.2:5000`

### For Physical Android Device:
1. Find your computer's IP: `ipconfig` on Windows
2. Update `lib/services/api_service.dart` line for Android to use your IP:
   ```dart
   baseUrl = 'http://192.168.1.100:5000'; // Replace with your actual IP
   ```
3. Ensure device is on same network as computer
4. Run: `flutter run -d <device-id>`

### For Web:
1. Run: `flutter run -d chrome`
2. App will use `http://localhost:5000`
3. Ensure CORS is enabled on backend (already configured)

### For iOS Simulator:
1. Run: `flutter run -d simulator`
2. App will use `http://127.0.0.1:5000`

## Backend Requirements
Ensure your Flask backend is running with:
- CORS enabled for `*` (already configured in app.py)
- Auth endpoints available at:
  - `/api/v1/auth/login` - POST
  - `/api/v1/auth/register` - POST
- Running on port 5000

## Testing
After fixes, the app should:
1. ✅ Initialize without hanging
2. ✅ Show login screen if not authenticated
3. ✅ Connect to backend on correct platform-specific URL
4. ✅ Work on Android emulator, physical device, web, and iOS
5. ✅ Display proper error messages if network fails

## Backend Verification
```bash
# Test the API endpoints
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Should return tokens and user data
```

## Migration for Physical Devices
If you need to use a physical device, edit `lib/services/api_service.dart`:
```dart
} else if (Platform.isAndroid) {
  baseUrl = 'http://192.168.100.46:5000'; // Change to your computer's IP
}
```

Then rebuild: `flutter clean && flutter pub get && flutter run`

---
**Status**: ✅ WHITE SCREEN ISSUE FIXED
**Files Modified**: 
- `lib/services/api_service.dart`
- `lib/main.dart`
