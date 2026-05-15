@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo  FIX ALL PRODUCT STATUS CHECKS
echo ========================================
echo.
echo Making 'active' products available...
echo.
py fix_all_product_status.py
echo.
pause
