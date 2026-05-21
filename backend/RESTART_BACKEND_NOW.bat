@echo off
echo ========================================
echo   RESTARTING BACKEND SERVER
echo ========================================
echo.
echo Stopping any running Flask processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting backend server...
cd /d "%~dp0"
start "Kids Backend Server" cmd /k "python app.py"

echo.
echo ========================================
echo   Backend server is starting...
echo   Check the new window for logs
echo ========================================
echo.
pause
