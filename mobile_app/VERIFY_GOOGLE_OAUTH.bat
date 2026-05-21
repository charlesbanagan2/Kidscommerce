@echo off
echo ========================================
echo Google OAuth Setup Verification
echo ========================================
echo.

echo [1/5] Checking Backend Configuration...
echo.
findstr "GOOGLE_OAUTH_CLIENT_ID" ..\backend\.env
echo.

echo [2/5] Checking Android Configuration...
echo.
if exist android\app\src\main\res\values\strings.xml (
    echo ✅ strings.xml exists
    type android\app\src\main\res\values\strings.xml | findstr "default_web_client_id"
) else (
    echo ❌ strings.xml NOT FOUND
)
echo.

echo [3/5] Checking Web Configuration...
echo.
if exist web\index.html (
    echo ✅ index.html exists
    type web\index.html | findstr "google-signin-client_id"
) else (
    echo ❌ index.html NOT FOUND
)
echo.

echo [4/5] Checking Flutter Configuration...
echo.
if exist lib\config\google_oauth_config.dart (
    echo ✅ google_oauth_config.dart exists
    type lib\config\google_oauth_config.dart | findstr "androidClientId"
    type lib\config\google_oauth_config.dart | findstr "webClientId"
) else (
    echo ❌ google_oauth_config.dart NOT FOUND
)
echo.

echo [5/5] Summary
echo ========================================
echo.
echo Client IDs Configured:
echo.
echo Android: 19725108081-d03cnmvghsfr3tpevj05pnn2upr55vds.apps.googleusercontent.com
echo Web:     19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com
echo.
echo ========================================
echo.
echo Next Steps:
echo 1. flutter clean
echo 2. flutter pub get
echo 3. flutter run
echo.
echo See GOOGLE_OAUTH_SETUP.md for details
echo.
pause
