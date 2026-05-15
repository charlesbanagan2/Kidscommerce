@echo off
cd C:\Users\mnban\Documents\kids
echo Applying FINAL fix for stock display...
.venv\Scripts\python.exe apply_final_fix.py
echo.
echo ============================================================
echo NOW RESTART FLASK:
echo 1. Press Ctrl+C in Flask terminal
echo 2. Run: python backend/app.py
echo ============================================================
pause
