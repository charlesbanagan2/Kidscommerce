# Backend Error Checking Guide

## Problema: "My Orders" at ibang tabs ay ayaw gumana

### Posibleng Dahilan:

1. **Database Connection Error**
2. **Session/Authentication Issue**
3. **Missing Data**
4. **JavaScript Error sa frontend**
5. **Backend Route Error**

## Paano I-check:

### Step 1: Tingnan ang Backend Terminal
Pagkatapos mag-click ng "My Orders", tingnan ang backend terminal window.

**Hanapin ang:**
- ❌ Error messages (red text)
- ❌ Traceback
- ❌ 500 Internal Server Error
- ❌ Database errors

**Example ng error:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection already closed
```

### Step 2: Check Browser Console
1. Press **F12** sa browser
2. Go to **Console** tab
3. Tingnan kung may error

**Common errors:**
- `Failed to fetch`
- `404 Not Found`
- `500 Internal Server Error`
- `Uncaught TypeError`

### Step 3: Check Network Tab
1. Press **F12** sa browser
2. Go to **Network** tab
3. Click "My Orders"
4. Tingnan ang requests

**Hanapin:**
- Red requests (failed)
- Status codes: 404, 500, 401
- Response body (click request → Response tab)

## Common Fixes:

### Fix 1: Restart Backend
Baka may stale connection or memory issue.

```bash
# Stop backend (Ctrl+C)
# Start again
python backend/app.py
```

### Fix 2: Check Database Connection
Baka nawala ang connection sa database.

**Check .env file:**
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

### Fix 3: Clear Browser Cache
Baka may cached na old JavaScript.

1. Press **Ctrl+Shift+Delete**
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page (**Ctrl+F5**)

### Fix 4: Check if Logged In
Baka nag-expire ang session.

1. Try to logout
2. Login again
3. Go to "My Orders"

### Fix 5: Check Database Data
Baka walang orders sa database.

Create test order:
1. Go to Shop
2. Add product to cart
3. Checkout
4. Check "My Orders" again

## Specific Error Solutions:

### Error: "StoreChatMessage is not defined"
✅ **FIXED** - Already updated in previous fixes

### Error: "RiderChatMessage is not defined"
✅ **FIXED** - Already updated in previous fixes

### Error: "Connection refused"
**Solution:**
1. Check if backend is running
2. Check IP address: `ipconfig`
3. Update `url_config.dart` if IP changed

### Error: "404 Not Found"
**Solution:**
1. Check if route exists in `app.py`
2. Check URL spelling
3. Restart backend

### Error: "500 Internal Server Error"
**Solution:**
1. Check backend terminal for error details
2. Check database connection
3. Check if all required columns exist

### Error: "Session expired" or "401 Unauthorized"
**Solution:**
1. Logout
2. Login again
3. Try again

## Debug Mode:

### Enable Detailed Logging
Edit `backend/app.py`, find:
```python
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
```

Already in debug mode! Errors should show in terminal.

### Add Print Statements
Sa `my_orders()` function, add:
```python
@app.route('/my-orders')
@login_required
def my_orders():
    print(f"[DEBUG] my_orders called by user {session['user_id']}")
    user_id = session['user_id']
    
    print(f"[DEBUG] Fetching orders for user {user_id}")
    all_orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()
    
    print(f"[DEBUG] Found {len(all_orders)} orders")
    # ... rest of code
```

## Testing Checklist:

- [ ] Backend is running (check terminal)
- [ ] No errors in backend terminal
- [ ] Browser console has no errors
- [ ] Network tab shows successful requests (200 status)
- [ ] User is logged in (check session)
- [ ] Database connection is working
- [ ] IP address is correct (172.20.10.12)
- [ ] Firewall port 5000 is open

## Quick Test Commands:

### Test if backend is accessible:
```bash
# In browser or curl
http://172.20.10.12:5000/
```

### Test if logged in:
```bash
# In browser console
console.log(document.cookie)
# Should show session cookie
```

### Test database connection:
```python
# In Python terminal
from backend.app import db
db.session.execute('SELECT 1')
# Should return result
```

## Ano ang Susunod na Gawin:

1. **I-run ang backend** - `python backend/app.py`
2. **I-open ang browser** - http://172.20.10.12:5000/
3. **Login** - Use test account
4. **Click "My Orders"**
5. **Tingnan ang terminal** - May error ba?
6. **Tingnan ang browser console (F12)** - May error ba?
7. **I-report ang error** - Copy-paste ang error message

## Need More Help?

Kung may specific error message, i-send mo sa akin para ma-fix ko agad.

**Format:**
```
Error location: [Backend/Frontend/Database]
Error message: [Copy-paste exact error]
What you were doing: [e.g., "Clicked My Orders tab"]
```
