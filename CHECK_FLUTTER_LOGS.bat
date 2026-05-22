@echo off
echo ========================================
echo FLUTTER APP DEBUG HELPER
echo ========================================
echo.

echo This will help you debug the loading issue.
echo.

echo Step 1: Check if backend is awake
echo Opening backend in browser...
start https://kids-kingdom.onrender.com
echo.
echo Wait for the page to load (may take 30-60 seconds if sleeping)
echo.
pause

echo.
echo Step 2: Test API endpoint
echo Opening products API...
start https://kids-kingdom.onrender.com/api/v1/products
echo.
echo Should show JSON data or 401 error (both OK)
echo Should NOT show 404 or connection error
echo.
pause

echo.
echo Step 3: Check Flutter config
echo Opening config file...
start notepad mobile_app\lib\config\url_config.dart
echo.
echo Check line 9: USE_LOCAL should be FALSE
echo Check line 17: URL should be https://kids-kingdom.onrender.com
echo.
pause

echo.
echo Step 4: Clear Flutter cache and run
echo.
cd mobile_app
echo Cleaning Flutter cache...
call flutter clean
echo.
echo Getting dependencies...
call flutter pub get
echo.
echo ========================================
echo Ready to run!
echo ========================================
echo.
echo Now run: flutter run
echo.
echo Watch the logs for:
echo - API errors (red text)
echo - Connection errors
echo - Timeout errors
echo - Auth errors
echo.
pause
