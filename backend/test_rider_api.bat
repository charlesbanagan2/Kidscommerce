@echo off
echo ========================================
echo Testing Rider API Endpoint
echo ========================================
echo.

echo Testing: GET /api/v1/rider/available-orders
echo.

curl -X GET "http://192.168.1.20:5000/api/v1/rider/available-orders" ^
  -H "Authorization: Bearer test_token" ^
  -H "Content-Type: application/json"

echo.
echo.
echo ========================================
echo Test Complete
echo ========================================
pause
