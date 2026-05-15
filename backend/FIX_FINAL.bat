@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo  FINAL WEB CART FIX
echo ========================================
echo.
py fix_web_final.py
echo.
echo Verifying all fixes...
echo.
py verify_fixes.py
echo.
pause
