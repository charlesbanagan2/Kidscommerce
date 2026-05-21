@echo off
echo ============================================================
echo Wishlist Persistence Test Suite
echo ============================================================
echo.

echo [1/3] Checking database structure...
echo.
cd backend
python check_wishlist_db.py
echo.
echo.

echo [2/3] Running automated API tests...
echo.
echo Make sure the backend server is running!
echo.
pause
python test_wishlist_api.py
echo.
echo.

echo [3/3] Test Summary
echo ============================================================
echo.
echo Database Check: Complete
echo API Tests: Complete
echo.
echo Next Steps:
echo 1. Review test results above
echo 2. Test mobile app manually (see TEST_WISHLIST_PERSISTENCE.md)
echo 3. Verify wishlist persists after logout/login
echo.
echo ============================================================
echo.
pause
