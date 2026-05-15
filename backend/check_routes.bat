@echo off
echo ========================================
echo Checking Backend Routes
echo ========================================
echo.

echo Testing health endpoint first...
curl -s http://192.168.1.20:5000/api/health
echo.
echo.

echo Testing rider available-orders endpoint...
curl -s http://192.168.1.20:5000/api/v1/rider/available-orders
echo.
echo.

echo ========================================
echo If you see HTML 404 above, the backend
echo needs to be restarted!
echo ========================================
pause
