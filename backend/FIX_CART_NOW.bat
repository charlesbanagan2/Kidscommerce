@echo off
echo ========================================
echo  CART DUPLICATE FIX - AUTO APPLY
echo ========================================
echo.
echo This will automatically fix all cart duplicate issues in app.py
echo A backup will be created before making changes.
echo.
pause

cd /d "%~dp0"

echo.
echo Running auto-fix script...
echo.

py auto_fix_cart.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying with 'python' command...
    python auto_fix_cart.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying with 'python3' command...
    python3 auto_fix_cart.py
)

echo.
echo ========================================
echo  DONE!
echo ========================================
echo.
echo If you see errors above, the fixes may not have been applied.
echo In that case, manually apply the fixes from APPLY_CART_FIXES.py
echo.
pause
