@echo off
echo ========================================
echo Allow Flask Port 5000 in Windows Firewall
echo ========================================
echo.

echo Adding firewall rule for port 5000...
netsh advfirewall firewall add rule name="Flask Backend Port 5000" dir=in action=allow protocol=TCP localport=5000

echo.
echo ========================================
echo Done! Port 5000 is now allowed.
echo ========================================
echo.
echo Now restart your Flask app:
echo   python app.py
echo.
echo Then test from phone browser:
echo   http://172.20.10.12:5000/api/health
echo.
pause
