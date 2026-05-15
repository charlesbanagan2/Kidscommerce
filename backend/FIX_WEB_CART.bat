@echo off
cd /d "%~dp0"
echo.
echo Fixing web cart functions...
echo.
py fix_web_cart.py
echo.
echo Now verifying...
echo.
py verify_fixes.py
echo.
pause
