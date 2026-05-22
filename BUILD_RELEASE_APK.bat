@echo off
echo ========================================
echo BUILD RELEASE APK FOR CLOUD
echo ========================================
echo.

echo This will build a standalone APK that works anywhere with internet.
echo.

echo Step 1: Checking config...
echo.
findstr /C:"USE_LOCAL = false" mobile_app\lib\config\url_config.dart >nul
if %errorlevel% equ 0 (
    echo ✅ Config is correct: USE_LOCAL = false
) else (
    echo ❌ ERROR: USE_LOCAL must be FALSE!
    echo.
    echo Please edit: mobile_app\lib\config\url_config.dart
    echo Change line 9 to: static const bool USE_LOCAL = false;
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Cleaning previous builds...
cd mobile_app
call flutter clean

echo.
echo Step 3: Getting dependencies...
call flutter pub get

echo.
echo Step 4: Building release APK...
echo This may take 2-5 minutes...
call flutter build apk --release

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo APK Location:
    echo mobile_app\build\app\outputs\flutter-apk\app-release.apk
    echo.
    echo Next Steps:
    echo 1. Copy APK to your phone
    echo 2. Install on phone
    echo 3. Open app - should work anywhere with internet!
    echo.
    echo Or run: flutter install (if phone is connected)
    echo.
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the error messages above.
    echo.
)

cd ..
pause
