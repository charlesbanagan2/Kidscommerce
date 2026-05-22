@echo off
echo ========================================
echo STARTING BACKEND SERVER (LOCAL HOTSPOT)
echo ========================================
echo.

echo Backend will be accessible at:
echo http://172.20.10.12:5000
echo.

echo Make sure:
echo 1. Mobile hotspot is ON
echo 2. Computer is connected to hotspot
echo 3. Firewall port 5000 is open (run ALLOW_MOBILE_CONNECTION.bat as Admin)
echo.

echo Starting backend server...
echo.

cd backend
python app.py

pause
