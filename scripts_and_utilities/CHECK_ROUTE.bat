@echo off
cd C:\Users\mnban\Documents\kids
.venv\Scripts\python.exe check_route.py > route_check.txt
type route_check.txt
echo.
echo Full output saved to route_check.txt and current_route.txt
pause
