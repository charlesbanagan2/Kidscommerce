@echo off
echo ================================================
echo Testing Forgot Password API
echo ================================================
echo.

echo Sending request to: http://192.168.1.20:5000/api/v1/auth/forgot-password
echo Email: malakaslang53@gmail.com
echo.

curl -X POST http://192.168.1.20:5000/api/v1/auth/forgot-password ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"malakaslang53@gmail.com\"}"

echo.
echo.
echo ================================================
echo Check the response above
echo If successful, check malakaslang53@gmail.com inbox
echo ================================================
pause
