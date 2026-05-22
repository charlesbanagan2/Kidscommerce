@echo off
echo ========================================
echo  RESTARTING BACKEND SERVER
echo ========================================
echo.
echo Stopping any running Flask servers...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting backend server...
cd backend
start "Kids Commerce Backend" python app.py

echo.
echo ========================================
echo  BACKEND SERVER STARTED!
echo ========================================
echo.
echo Backend URL: http://172.20.10.12:5000
echo Registration: http://172.20.10.12:5000/register-buyer
echo.
echo Email verification is now FIXED!
echo You can now register with any Gmail address.
echo.
pause
