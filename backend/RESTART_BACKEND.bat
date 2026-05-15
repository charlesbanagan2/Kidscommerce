@echo off
echo ========================================
echo RESTARTING FLASK BACKEND SERVER
echo ========================================
echo.
echo IMPORTANT: This will stop any running Flask server
echo and start a new one with the updated rider API routes.
echo.
echo Press CTRL+C to stop this script
echo.
pause

cd /d c:\Users\mnban\Documents\kids\backend

echo.
echo Stopping any existing Flask processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Flask*" 2>nul

echo.
echo Starting Flask server...
echo.
python app.py
