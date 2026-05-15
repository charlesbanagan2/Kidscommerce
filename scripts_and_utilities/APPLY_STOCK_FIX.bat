@echo off
echo ================================================================================
echo APPLYING STOCK SYNCHRONIZATION FIX
echo ================================================================================
echo.
echo This will make stock values consistent across:
echo   - Database (product.stock)
echo   - Website (Flask templates)
echo   - Mobile App (API response)
echo.
echo ================================================================================
echo.

echo The fix ensures that if database shows stock = 100, then:
echo   - Website shows: 100
echo   - API returns: 100
echo   - Mobile app displays: 100
echo.
echo ================================================================================
echo WHAT NEEDS TO BE CHANGED:
echo ================================================================================
echo.
echo 1. Backend API endpoint /api/products
echo    Change: 'stock': get_available_stock(product.id)
echo    To:     'stock': product.stock
echo.
echo 2. Website templates (product_detail.html, shop.html)
echo    Change: {{ get_available_stock(product.id) }}
echo    To:     {{ product.stock }}
echo.
echo 3. Mobile app (NO CHANGE NEEDED - already correct)
echo    It reads: stock: json['stock']
echo.
echo ================================================================================
echo.
echo To apply this fix manually:
echo.
echo 1. Open: backend\app.py
echo    Search for: @app.route('/api/products')
echo    Find the line with: 'stock': get_available_stock
echo    Change to: 'stock': p.stock or product.stock
echo.
echo 2. Open: backend\templates\product_detail.html
echo    Search for: get_available_stock
echo    Replace with: product.stock
echo.
echo 3. Open: backend\templates\shop.html  
echo    Search for: get_available_stock
echo    Replace with: product.stock
echo.
echo 4. Restart Flask backend
echo.
echo 5. Test:
echo    - Visit website product page
echo    - Check API: http://localhost:5000/api/products
echo    - Open mobile app
echo    - All should show SAME stock value
echo.
echo ================================================================================
echo.
pause
