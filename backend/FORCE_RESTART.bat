@echo off
echo ========================================
echo FORCE RESTART FLASK BACKEND SERVER
echo ========================================
echo.

cd /d c:\Users\mnban\Documents\kids\backend

echo Killing all Python processes on port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Starting Flask server...
echo.
echo ========================================
echo LOOK FOR THIS MESSAGE:
echo "✅ Rider mobile API routes loaded successfully"
echo ========================================
echo.

python app.py
