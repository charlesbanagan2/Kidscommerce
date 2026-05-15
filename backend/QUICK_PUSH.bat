@echo off
echo ========================================
echo  QUICK PUSH TO GITHUB (Auto-Deploy)
echo ========================================
echo.

cd /d c:\Users\mnban\Documents\kids\backend

echo What did you change? (e.g., "Fixed login bug")
set /p message="Commit message: "

echo.
echo Adding files...
git add .

echo Committing changes...
git commit -m "%message%"

echo Pushing to GitHub...
git push

echo.
echo ========================================
echo  DONE! Render will auto-deploy in 2-3 min
echo ========================================
echo.
pause
