@echo off
cd C:\Users\mnban\Documents\kids
echo Testing product_detail route logic...
echo.
.venv\Scripts\python.exe test_route_logic.py
echo.
echo ============================================================
echo If all products show IN STOCK and have images, the fix works!
echo Now restart Flask and test in browser.
echo ============================================================
pause
