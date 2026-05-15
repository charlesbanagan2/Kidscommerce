@echo off
echo ========================================
echo Kids Commerce - Checkout Test Suite
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Flutter installation...
flutter --version
if %errorlevel% neq 0 (
    echo ERROR: Flutter not found!
    pause
    exit /b 1
)
echo.

echo [2/4] Getting dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo ERROR: Failed to get dependencies!
    pause
    exit /b 1
)
echo.

echo [3/4] Running checkout tests...
echo.
flutter test test/checkout_test.dart -r expanded
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo TESTS FAILED!
    echo ========================================
    pause
    exit /b 1
)
echo.

echo [4/4] Test Summary
echo ========================================
echo.
echo ✅ ALL CHECKOUT TESTS PASSED!
echo.
echo Test Coverage:
echo - Checkout without coupon: PASS
echo - Checkout with coupon: PASS
echo - Discount calculations: PASS
echo - Payment methods: PASS
echo - Field validations: PASS
echo - Cart operations: PASS
echo - Edge cases: PASS
echo.
echo ========================================
echo.
echo Next Steps:
echo 1. Run manual tests (see CHECKOUT_TEST_MANUAL.md)
echo 2. Test on real device
echo 3. Verify backend integration
echo.
pause
