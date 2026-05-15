@echo off
echo ============================================================
echo PRODUCT CHAT API TEST
echo ============================================================

echo.
echo === Step 1: Testing Health Check ===
curl -X GET http://localhost:5000/api/health
echo.

echo.
echo === Step 2: Testing Login (admin) ===
curl -X POST http://localhost:5000/api/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@kidscommerce.com\",\"password\":\"admin123\"}"
echo.

echo.
echo === Step 3: Testing Product Chat Start (with token) ===
echo Please copy the access_token from above and run:
echo curl -X POST http://localhost:5000/api/v1/chat/product/start ^
echo   -H "Content-Type: application/json" ^
echo   -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
echo   -d "{\"product_id\":1,\"message\":\"Hi! I'm interested in this product\"}"
echo.

echo.
echo ============================================================
echo TEST SCRIPT READY
echo ============================================================
pause
