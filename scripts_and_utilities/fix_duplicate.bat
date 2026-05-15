@echo off
echo Finding duplicate product_detail route...
echo.
C:\Users\mnban\Documents\kids\.venv\Scripts\python.exe C:\Users\mnban\Documents\kids\show_duplicate.py
echo.
echo Check line_7874_context.txt to see what will be removed
echo.
echo Press any key to REMOVE the duplicate, or close this window to cancel
pause
echo.
echo Removing duplicate...
C:\Users\mnban\Documents\kids\.venv\Scripts\python.exe C:\Users\mnban\Documents\kids\REMOVE_DUPLICATE.py
