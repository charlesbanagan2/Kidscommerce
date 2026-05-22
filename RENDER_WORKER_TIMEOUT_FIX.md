# 🚨 RENDER WORKER TIMEOUT - KAILANGAN I-FIX! 🚨

## Problema sa Render Deployment

Ang deployment ay **SUCCESSFUL** pero may **WORKER TIMEOUT** error:

```
[CRITICAL] WORKER TIMEOUT (pid:213)
[ERROR] Error handling request /my-orders
SystemExit: 1
```

### Bakit Nangyayari Ito?

**Mali ang Gunicorn worker type!**

- **Current (MALI):** `gunicorn app:app` - uses **sync workers**
- **Dapat:** `gunicorn --worker-class eventlet -w 1 wsgi:app` - uses **eventlet workers**

**Sync workers** = Hindi kaya ang Flask-SocketIO at long-running requests (timeout after 30 seconds)
**Eventlet workers** = Async, kaya ang SocketIO, walang timeout issues

---

## ⚡ SOLUTION: Update Render Start Command

### Step 1: Login to Render Dashboard

```
https://dashboard.render.com/
```

### Step 2: Go to Your Service Settings

1. Click: **kids-kingdom** (or your service name)
2. Click: **Settings** tab (left sidebar)
3. Scroll down to: **Build & Deploy** section

### Step 3: Update Start Command

Find the **Start Command** field and **REPLACE** with:

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

**IMPORTANT:** Copy-paste exactly! No typos!

### Step 4: Save and Redeploy

1. Click: **Save Changes** (blue button at bottom)
2. Render will automatically redeploy
3. Wait 3-4 minutes for deployment to complete

---

## 📋 What This Command Does

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

- `gunicorn` - Production WSGI server
- `--worker-class eventlet` - Use async eventlet workers (needed for SocketIO)
- `-w 1` - Use 1 worker (Render free tier has limited memory)
- `--bind 0.0.0.0:10000` - Listen on all interfaces, port 10000 (Render default)
- `wsgi:app` - Load app from wsgi.py file

---

## ✅ How to Verify It's Fixed

### 1. Check Deployment Logs

After redeploying, you should see in the logs:

```
✅ Starting service with 'gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app'
✅ [INFO] Using worker: eventlet
✅ [INFO] Booting worker with pid: XXXX
✅ [INFO] Listening at: http://0.0.0.0:10000
```

**NOT:**
```
❌ Running 'gunicorn app:app'
❌ [CRITICAL] WORKER TIMEOUT
```

### 2. Test the Endpoints

Once deployment shows "Live", test these URLs:

**Homepage:**
```
https://kids-kingdom.onrender.com/
```
Should return: "Kids Kingdom API is running"

**Health Check:**
```
https://kids-kingdom.onrender.com/api/v1/health
```
Should return: `{"status": "healthy"}`

**Products API:**
```
https://kids-kingdom.onrender.com/api/products
```
Should return: Product list (JSON)

**My Orders (Previously Timing Out):**
```
https://kids-kingdom.onrender.com/my-orders
```
Should return: Orders page (no timeout!)

### 3. Test from Mobile App

Update `mobile_app/lib/config/url_config.dart`:

```dart
class UrlConfig {
  static const String baseUrl = 'https://kids-kingdom.onrender.com';
  // ... rest of config
}
```

Then test:
- Registration
- Login
- Browse products
- Place order
- View orders (this was timing out before!)

---

## 🔍 Why Was It Timing Out?

### The Problem Chain:

1. **Sync worker** receives request to `/my-orders`
2. Code calls `get_data()` which makes HTTPS request to Supabase
3. **SSL certificate loading** takes time
4. Sync worker **blocks** waiting for response
5. After **30 seconds**, Gunicorn kills the worker (WORKER TIMEOUT)
6. Request fails with **500 error**

### The Solution:

1. **Eventlet worker** receives request to `/my-orders`
2. Code calls `get_data()` which makes HTTPS request to Supabase
3. **Eventlet worker** doesn't block - handles other requests while waiting
4. **No timeout** - worker stays alive
5. Response returns successfully
6. Request succeeds with **200 OK**

---

## 📸 Visual Guide: Where to Update

```
Render Dashboard
  └─ kids-kingdom (your service)
      └─ Settings (left sidebar)
          └─ Build & Deploy section
              └─ Start Command field
                  └─ PASTE HERE: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

---

## ⏱️ Timeline

- **Login to Render:** 10 seconds
- **Navigate to Settings:** 10 seconds
- **Update Start Command:** 20 seconds
- **Save Changes:** Instant
- **Redeploy:** 3-4 minutes
- **Test:** 1 minute

**Total: ~5 minutes** to fix completely!

---

## 🆘 Troubleshooting

### Problem: Can't find Start Command field

**Solution:**
- Make sure you're in the **Settings** tab (not Environment or Logs)
- Scroll down - it's in the **Build & Deploy** section
- Look for "Start Command" or "Run Command"

### Problem: Getting "eventlet not found" error

**Solution:**
- Check `requirements.txt` includes: `eventlet==0.37.0`
- It should already be there (we added it)
- If not, add it and redeploy

### Problem: Still getting timeout after update

**Solution:**
1. Verify the command was saved correctly
2. Check logs to confirm eventlet worker is being used
3. Try increasing worker timeout:
   ```bash
   gunicorn --worker-class eventlet -w 1 --timeout 120 --bind 0.0.0.0:10000 wsgi:app
   ```

### Problem: 502 Bad Gateway

**Solution:**
- Wait a few more minutes - deployment might still be in progress
- Check logs for errors
- Verify environment variables are all set

---

## 📝 Checklist

Before marking as complete:

- [ ] Logged into Render Dashboard
- [ ] Found Start Command field in Settings
- [ ] Updated command to use eventlet worker
- [ ] Saved changes
- [ ] Waited for redeploy to complete
- [ ] Checked logs - no more WORKER TIMEOUT
- [ ] Tested homepage - works
- [ ] Tested API endpoints - return data
- [ ] Tested /my-orders - no timeout
- [ ] Updated mobile app URL config
- [ ] Tested mobile app - connects successfully

---

## 🎯 DO THIS NOW!

### Quick Steps:

1. **Open:** https://dashboard.render.com/
2. **Click:** Your service → Settings
3. **Find:** Start Command field
4. **Paste:** `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app`
5. **Click:** Save Changes
6. **Wait:** 3-4 minutes for redeploy
7. **Test:** https://kids-kingdom.onrender.com/

**That's it! Simple dashboard update lang!** 🚀

---

## 📚 Related Files

- `backend/wsgi.py` - Entry point for Gunicorn ✅
- `backend/requirements.txt` - Includes eventlet ✅
- `backend/app.py` - Flask app with SocketIO ✅
- `RENDER_ENV_VARS.txt` - Environment variables (already set) ✅

Everything is ready - just need to update the start command!

---

**Status:** ⚠️ **ACTION REQUIRED** - Update Render Start Command

**Priority:** 🔴 **HIGH** - Blocking production deployment

**Time to Fix:** ⏱️ **5 minutes**

**Last Updated:** May 22, 2026
