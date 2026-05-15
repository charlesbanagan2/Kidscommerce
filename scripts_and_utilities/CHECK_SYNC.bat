@echo off
echo ================================================================================
echo CHECKING PRICE AND STOCK SYNC
echo ================================================================================
echo.

cd /d "%~dp0"

REM Try different Python commands
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python check_sync.py
    goto :end
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py check_sync.py
    goto :end
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python3 check_sync.py
    goto :end
)

echo ERROR: Python not found in PATH
echo.
echo Please install Python or add it to your PATH environment variable.
echo Download from: https://www.python.org/downloads/
echo.
pause
goto :end

:end
echo.
echo ================================================================================
echo.
pause
