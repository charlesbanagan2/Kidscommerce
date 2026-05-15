@echo off
echo ============================================================
echo   Starting Kids Commerce Backend Server
echo ============================================================
echo.

cd /d "%~dp0"

echo Checking Python environment...
python --version
echo.

echo Starting Flask server on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause
