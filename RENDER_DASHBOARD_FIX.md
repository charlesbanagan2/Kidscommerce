# URGENT: Render Dashboard Configuration Fix

## Problem

Ang deployment ay nag-fail dahil Render is using the WRONG start command:

**What Render is running:**
```
gunicorn app:app
```

**What it SHOULD run (from render.yaml):**
```
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

## Root Cause

Ang Render dashboard may have a **manual start command configured** na nag-override ng render.yaml file.

## Solution: Update Render Dashboard Settings

### Step 1: Go to Render Dashboard

1. Open: https://dashboard.render.com/
2. Click on: **kids-ecommerce-api** service
3. Click on: **Settings** tab (left sidebar)

### Step 2: Update Start Command

Scroll down to **Build & Deploy** section:

1. Find: **Start Command** field
2. **CLEAR** the existing command (if any)
3. **PASTE** this exact command:
   ```
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
   ```
4. Click: **Save Changes** button

### Step 3: Manual Deploy

After saving:

1. Go to: **Manual Deploy** section (top right)
2. Click: **Deploy latest commit**
3. Wait for deployment to complete

## Alternative: Use render.yaml (Recommended)

If you want Render to automatically use render.yaml:

### Step 1: Clear Manual Start Command

1. Go to: Settings → Build & Deploy
2. Find: **Start Command** field
3. **DELETE/CLEAR** everything in that field
4. Click: **Save Changes**

### Step 2: Verify render.yaml is detected

1. Go to: Settings → General
2. Check if **"Using render.yaml"** is shown
3. If not, you may need to specify the path: `backend/render.yaml`

### Step 3: Redeploy

1. Click: **Manual Deploy** → **Deploy latest commit**
2. Watch logs for correct command

## What to Look For in Logs

### ✅ SUCCESS - You should see:

```
==> Starting service with 'gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app'
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Using worker: eventlet
[INFO] Booting worker with pid: XXXX
```

### ❌ FAILURE - If you see:

```
==> Running 'gunicorn app:app'
```

This means the dashboard setting is still overriding render.yaml.

## Quick Fix Commands (If Dashboard Not Working)

If you can't access dashboard, update via Render CLI:

```bash
# Install Render CLI (if not installed)
npm install -g @render/cli

# Login
render login

# Update start command
render services update kids-ecommerce-api \
  --start-command "gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app"
```

## Why This Matters

The correct command includes:
- `--worker-class eventlet` → Enables WebSocket support for Flask-SocketIO
- `-w 1` → Single worker (required for SocketIO)
- `--bind 0.0.0.0:10000` → Binds to Render's port
- `wsgi:app` → Uses our wsgi.py that exports socketio

Without these, the app will:
- ❌ Return 404 on all routes
- ❌ Fail to start properly
- ❌ Not support WebSocket connections

## Verification After Fix

After updating and redeploying, test:

1. **Check logs for correct command**
2. **Wait for "Live" status**
3. **Test URLs:**
   - https://kidscommerce-backend.onrender.com/
   - https://kidscommerce-backend.onrender.com/api/health
   - https://kidscommerce-backend.onrender.com/api/products

All should return data (NOT 404).

## Summary

**Action Required:**
1. Go to Render Dashboard → Settings
2. Update Start Command to: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app`
3. Save and redeploy
4. Verify in logs that correct command is used

**DO THIS NOW** to fix the deployment! 🚀
