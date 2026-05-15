@echo off
REM Quick Setup Script for Notification Optimizations
REM Run this in your backend directory

echo ========================================
echo NOTIFICATION OPTIMIZATION SETUP
echo ========================================
echo.

echo Step 1: Installing Redis Python client...
pip install redis hiredis
echo.

echo Step 2: Checking if .env file exists...
if exist .env (
    echo .env file found
    echo.
    echo Please add these lines to your .env file:
    echo.
    echo REDIS_CACHE_ENABLED=true
    echo REDIS_URL=redis://localhost:6379/0
    echo.
) else (
    echo WARNING: .env file not found!
    echo Please create .env file with Redis configuration
)

echo.
echo Step 3: Database Indexes
echo ========================================
echo.
echo IMPORTANT: You must run the SQL script in Supabase!
echo.
echo 1. Open Supabase Dashboard
echo 2. Go to SQL Editor
echo 3. Open: create_notification_indexes.sql
echo 4. Click Run
echo.
echo This will create indexes for fast queries.
echo.

echo Step 4: Redis Setup (Optional but Recommended)
echo ========================================
echo.
echo Option A - Local Redis (Development):
echo   1. Download Redis from: https://github.com/microsoftarchive/redis/releases
echo   2. Install and run redis-server.exe
echo   3. Set REDIS_URL=redis://localhost:6379/0 in .env
echo.
echo Option B - Upstash Redis (Production - FREE):
echo   1. Sign up at: https://upstash.com
echo   2. Create a Redis database
echo   3. Copy the Redis URL
echo   4. Set REDIS_URL in .env
echo.
echo Option C - No Redis:
echo   Set REDIS_CACHE_ENABLED=false in .env
echo   (Still fast with database indexes)
echo.

echo ========================================
echo SETUP COMPLETE
echo ========================================
echo.
echo Next Steps:
echo 1. Run SQL indexes in Supabase (REQUIRED)
echo 2. Configure Redis in .env (OPTIONAL)
echo 3. Restart your Flask application
echo 4. Run: python test_optimization.py
echo.
echo See OPTIMIZATION_GUIDE.md for detailed instructions
echo.
pause
