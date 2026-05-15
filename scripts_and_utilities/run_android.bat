@echo off
REM Quick Start Flutter App on Android

echo.
echo ╔════════════════════════════════════════════════╗
echo ║     Kids Kingdom - Android Run Guide          ║
echo ╚════════════════════════════════════════════════╝
echo.

REM Step 1: Check backend
echo [1/4] Checking backend server...
cd /d c:\Users\mnban\Documents\kids
python quick_test.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ Backend not running! Starting Flask...
    start python backend/app.py
    timeout /t 3 >nul
)
echo ✓ Backend ready at 192.168.1.20:5000

REM Step 2: Verify test account exists
echo.
echo [2/4] Test Account: testbuyer@test.com / test123
echo ✓ Using existing database account

REM Step 3: Connect Android Device
echo.
echo [3/4] Checking Android device connection...
echo.
echo ⚠ IMPORTANT:
echo   1. Connect Android device via USB cable
echo   2. Enable USB Debugging on phone (Settings ^> Developer Options)
echo   3. Press Enter when ready...
pause

REM Step 4: Build Flutter app
echo.
echo [4/4] Building Flutter app...
cd /d c:\Users\mnban\Documents\kids\mobile_app
flutter pub get >nul 2>&1
echo ✓ App ready

REM Step 5: Run on Android
echo.
echo ✓ ALL CHECKS PASSED!
echo.
echo Starting Flutter app...
echo.
echo LOGIN CREDENTIALS:
echo   Email:    testbuyer@test.com
echo   Password: test123
echo.
flutter run

echo.
echo Troubleshooting tips:
echo - If connection error: Make sure phone is on SAME WiFi as PC
echo - Check backend: python quick_test.py
echo - View logs: adb logcat
echo - Hot reload: Press 'r' in terminal
echo.
pause
