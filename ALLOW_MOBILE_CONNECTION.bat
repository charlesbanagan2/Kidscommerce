@echo off
echo ========================================
echo ALLOW MOBILE APP TO CONNECT TO BACKEND
echo ========================================
echo.

echo This will open Windows Firewall port 5000
echo so your phone can connect to the backend.
echo.
echo You need to run tahis as ADMINISTRATOR!
echo.
pause

echo.
echo [1/2] Adding Firewall Rule for Port 5000...
netsh advfirewall firewall add rule name="Kids Commerce Backend Port 5000" dir=in action=allow protocol=TCP localport=5000

echo.
echo [2/2] Verifying Rule...
netsh advfirewall firewall show rule name="Kids Commerce Backend Port 5000"

echo.
echo ========================================
echo DONE! Port 5000 is now open.
echo ========================================
echo.
echo Your phone can now connect to:
echo http://192.168.1.26:5000
echo.
echo Make sure:
echo 1. Backend is running (python backend/app.py)
echo 2. Phone is on same WiFi network
echo 3. Restart Flutter app
echo.
pause
