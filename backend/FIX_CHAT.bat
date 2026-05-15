@echo off
echo ============================================================
echo   FIXING CHAT SYSTEM - Please Wait...
echo ============================================================
echo.

cd /d "%~dp0"

python fix_chat_system.py

echo.
echo ============================================================
echo   Fix Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Restart your Flask server (Ctrl+C then python app.py)
echo 2. Run tests: python test_chat_system.py
echo.

pause
