@echo off
REM ============================================
REM RIDER SYSTEM - COMPLETE FIX SCRIPT
REM Applies all necessary fixes automatically
REM ============================================

echo.
echo ============================================
echo RIDER SYSTEM - AUTOMATED FIX
echo ============================================
echo.

cd /d "%~dp0\backend"

echo [Step 1/6] Backing up old API files...
if exist rider_complete_api.py (
    ren rider_complete_api.py rider_complete_api.py.OLD
    echo   - Renamed rider_complete_api.py to .OLD
)
if exist rider_api.py (
    ren rider_api.py rider_api.py.OLD
    echo   - Renamed rider_api.py to .OLD
)
echo.

echo [Step 2/6] Applying fixed API file...
if exist rider_mobile_only_api_FIXED.py (
    copy /Y rider_mobile_only_api_FIXED.py rider_mobile_only_api.py
    echo   - Applied fixed rider_mobile_only_api.py
) else (
    echo   - WARNING: rider_mobile_only_api_FIXED.py not found
)
echo.

echo [Step 3/6] Checking app.py configuration...
findstr /C:"from rider_mobile_only_api import" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   - Rider API import already exists in app.py
) else (
    echo   - WARNING: Rider API import NOT found in app.py
    echo   - You need to add this line to app.py:
    echo     from rider_mobile_only_api import *
)
echo.

findstr /C:"from chat_complete_api import" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   - Chat API import already exists in app.py
) else (
    echo   - WARNING: Chat API import NOT found in app.py
    echo   - You need to add this line to app.py:
    echo     from chat_complete_api import *
)
echo.

findstr /C:"socketio = SocketIO" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   - Socket.IO initialization found in app.py
) else (
    echo   - WARNING: Socket.IO initialization NOT found
    echo   - You need to add this line to app.py:
    echo     socketio = SocketIO(app, cors_allowed_origins="*")
)
echo.

findstr /C:"socketio.run(app" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   - socketio.run() found in app.py
) else (
    echo   - WARNING: Using app.run() instead of socketio.run()
    echo   - Change to: socketio.run(app, host='0.0.0.0', port=5000)
)
echo.

echo [Step 4/6] Checking database configuration...
findstr /C:"postgresql://" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   - PostgreSQL database detected
) else (
    findstr /C:"sqlite:///" app.py >nul 2>&1
    if %errorlevel% equ 0 (
        echo   - WARNING: SQLite database detected
        echo   - FCFS row-level locking requires PostgreSQL!
    ) else (
        echo   - WARNING: Database configuration not found
    )
)
echo.

echo [Step 5/6] Creating app.py additions file...
echo # ============================================ > app_py_additions.txt
echo # ADD THESE LINES TO app.py >> app_py_additions.txt
echo # ============================================ >> app_py_additions.txt
echo. >> app_py_additions.txt
echo # 1. Add at the top with other imports: >> app_py_additions.txt
echo from flask_socketio import SocketIO, emit, join_room, leave_room >> app_py_additions.txt
echo. >> app_py_additions.txt
echo # 2. Add after Flask app initialization: >> app_py_additions.txt
echo socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading') >> app_py_additions.txt
echo. >> app_py_additions.txt
echo # 3. Add before if __name__ == '__main__': >> app_py_additions.txt
echo from rider_mobile_only_api import * >> app_py_additions.txt
echo from chat_complete_api import * >> app_py_additions.txt
echo. >> app_py_additions.txt
echo # 4. Change app.run() to: >> app_py_additions.txt
echo if __name__ == '__main__': >> app_py_additions.txt
echo     socketio.run(app, host='0.0.0.0', port=5000, debug=True) >> app_py_additions.txt
echo. >> app_py_additions.txt
echo   - Created app_py_additions.txt with required code
echo.

echo [Step 6/6] Creating database migration script...
echo # ============================================ > apply_db_migrations.sql
echo # DATABASE MIGRATIONS FOR RIDER SYSTEM >> apply_db_migrations.sql
echo # Run this in your PostgreSQL database >> apply_db_migrations.sql
echo # ============================================ >> apply_db_migrations.sql
echo. >> apply_db_migrations.sql
echo -- Add rider columns to Order table >> apply_db_migrations.sql
echo ALTER TABLE "order" ADD COLUMN IF NOT EXISTS rider_id INTEGER; >> apply_db_migrations.sql
echo ALTER TABLE "order" ADD COLUMN IF NOT EXISTS picked_up_at TIMESTAMP; >> apply_db_migrations.sql
echo ALTER TABLE "order" ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP; >> apply_db_migrations.sql
echo ALTER TABLE "order" ADD COLUMN IF NOT EXISTS rider_earnings FLOAT DEFAULT 0.0; >> apply_db_migrations.sql
echo. >> apply_db_migrations.sql
echo -- Create rider_details table >> apply_db_migrations.sql
echo CREATE TABLE IF NOT EXISTS rider_details ( >> apply_db_migrations.sql
echo     id SERIAL PRIMARY KEY, >> apply_db_migrations.sql
echo     user_id INTEGER REFERENCES "user"(id), >> apply_db_migrations.sql
echo     vehicle_type VARCHAR(50), >> apply_db_migrations.sql
echo     vehicle_model VARCHAR(100), >> apply_db_migrations.sql
echo     plate_number VARCHAR(20), >> apply_db_migrations.sql
echo     valid_id_front VARCHAR(255), >> apply_db_migrations.sql
echo     valid_id_back VARCHAR(255), >> apply_db_migrations.sql
echo     drivers_license VARCHAR(255), >> apply_db_migrations.sql
echo     status VARCHAR(20) DEFAULT 'pending', >> apply_db_migrations.sql
echo     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, >> apply_db_migrations.sql
echo     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP >> apply_db_migrations.sql
echo ); >> apply_db_migrations.sql
echo. >> apply_db_migrations.sql
echo -- Create chat_message table >> apply_db_migrations.sql
echo CREATE TABLE IF NOT EXISTS chat_message ( >> apply_db_migrations.sql
echo     id SERIAL PRIMARY KEY, >> apply_db_migrations.sql
echo     sender_id INTEGER REFERENCES "user"(id), >> apply_db_migrations.sql
echo     receiver_id INTEGER REFERENCES "user"(id), >> apply_db_migrations.sql
echo     message TEXT NOT NULL, >> apply_db_migrations.sql
echo     is_read BOOLEAN DEFAULT FALSE, >> apply_db_migrations.sql
echo     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, >> apply_db_migrations.sql
echo     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP >> apply_db_migrations.sql
echo ); >> apply_db_migrations.sql
echo. >> apply_db_migrations.sql
echo CREATE INDEX IF NOT EXISTS idx_chat_sender ON chat_message(sender_id); >> apply_db_migrations.sql
echo CREATE INDEX IF NOT EXISTS idx_chat_receiver ON chat_message(receiver_id); >> apply_db_migrations.sql
echo CREATE INDEX IF NOT EXISTS idx_chat_is_read ON chat_message(is_read); >> apply_db_migrations.sql
echo. >> apply_db_migrations.sql
echo   - Created apply_db_migrations.sql
echo.

echo ============================================
echo FIX APPLICATION COMPLETE
echo ============================================
echo.
echo NEXT STEPS:
echo.
echo 1. MANUAL: Edit app.py and add the code from app_py_additions.txt
echo    Location: backend\app_py_additions.txt
echo.
echo 2. MANUAL: Run database migrations
echo    psql -U postgres -d kids_ecommerce -f apply_db_migrations.sql
echo.
echo 3. TEST: Start the backend
echo    python app.py
echo.
echo 4. TEST: Run automated tests
echo    python ..\test_rider_workflow.py
echo.
echo See QUICK_START.md for detailed instructions
echo.
pause
