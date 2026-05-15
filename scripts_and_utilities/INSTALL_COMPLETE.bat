@echo off
cd C:\Users\mnban\Documents\kids
echo Installing COMPLETE product_detail route with ALL variables...
echo.
.venv\Scripts\python.exe install_complete.py
echo.
echo Done! Now restart Flask: python backend/app.py
pause
