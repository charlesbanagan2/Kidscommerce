@echo off
cd /d "%~dp0"
py find_status_checks.py > status_checks.txt
type status_checks.txt
echo.
echo Results saved to status_checks.txt
pause
