# 🚨 CLEAR BUILD CACHE - GAWIN NGAYON! 🚨

## Problema

Render is using **OLD cached build** with sync workers!

```
==> Running 'gunicorn app:app'  ← OLD COMMAND!
[INFO] Using worker: sync  ← WRONG! Will timeout!
```

---

## ✅ SOLUTION: Clear Cache + Update Command

### STEP 1: Update Start Command

1. Go to: **https://dashboard.render.com/**
2. Click: **kids-kingdom** service
3. Click: **Settings** (left sidebar)
4. Scroll to: **Build & Deploy** section
5. Find: **Start Command** field
6. **DELETE everything and paste this:**

```bash
gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:10000 wsgi:app
```

7. **IMPORTANT:** Make sure it says `gevent` not `eventlet`!
8. Click: **Save Changes** (blue button at bottom)

### STEP 2: Clear Build Cache & Deploy

**Still in Settings page:**

1. Scroll down to: **Danger Zone** or **Build & Deploy** section
2. Find: **Clear build cache** button
3. Click: **Clear build cache & deploy**
4. Confirm: Click **Yes, clear cache and deploy**
5. Wait: **4-5 minutes** (longer because clearing cache)

---

## ✅ What This Does

### Clear Build Cache:
- Deletes old Python 3.14 environment
- Deletes old eventlet installation
- Forces fresh install of everything

### Fresh Deploy:
- Installs Python 3.11 (from runtime.txt)
- Installs gevent (from requirements.txt)
- Uses new Start Command with gevent worker

---

## ✅ Expected Logs

### During Build:

```
✅ Detected runtime: python-3.11.9
✅ Installing Python 3.11.9
✅ Installing dependencies from requirements.txt
✅ Collecting gevent==24.2.1
✅ Collecting gevent-websocket==0.10.1
✅ Successfully installed gevent-24.2.1 gevent-websocket-0.10.1
```

### During Start:

```
✅ Running 'gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:10000 wsgi:app'
✅ Starting gunicorn 23.0.0
✅ Using worker: gevent  ← CORRECT!
✅ Booting worker with pid: 44
✅ Listening at: http://0.0.0.0:10000
```

### NOT:

```
❌ Running 'gunicorn app:app'
❌ Using worker: sync
❌ AttributeError: ... 'start_joinable_thread'
```

---

## 🎯 Visual Guide

### Where to Find Clear Build Cache:

```
Render Dashboard
  └─ kids-kingdom
      └─ Settings (left sidebar)
          └─ Scroll down
              └─ Build & Deploy section
                  ├─ Start Command: [UPDATE THIS FIRST!]
                  │   └─ gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:10000 wsgi:app
                  │
                  └─ Clear build cache & deploy [CLICK THIS!]
```

---

## 📋 Step-by-Step Checklist

- [ ] **Step 1:** Opened Render Dashboard
- [ ] **Step 2:** Clicked kids-kingdom service
- [ ] **Step 3:** Clicked Settings tab
- [ ] **Step 4:** Found Start Command field
- [ ] **Step 5:** Deleted old command
- [ ] **Step 6:** Pasted new command with `gevent`
- [ ] **Step 7:** Verified it says `gevent` (not eventlet or sync)
- [ ] **Step 8:** Clicked Save Changes
- [ ] **Step 9:** Scrolled down to find Clear build cache
- [ ] **Step 10:** Clicked Clear build cache & deploy
- [ ] **Step 11:** Confirmed the action
- [ ] **Step 12:** Waited 4-5 minutes
- [ ] **Step 13:** Checked logs - Python 3.11 installed ✅
- [ ] **Step 14:** Checked logs - gevent installed ✅
- [ ] **Step 15:** Checked logs - gevent worker running ✅
- [ ] **Step 16:** Tested URL - works! ✅

---

## 🆘 Troubleshooting

### Problem: Can't find "Clear build cache" button

**Solution:**
- Make sure you're in **Settings** tab
- Scroll all the way down
- Look for "Danger Zone" or "Build & Deploy" section
- Button might say "Clear build cache & deploy" or just "Clear cache"

### Problem: Start Command field is empty or disabled

**Solution:**
- Make sure you're editing the correct service (kids-kingdom)
- Try refreshing the page
- Make sure you have permission to edit settings

### Problem: Still getting sync worker after clearing cache

**Solution:**
1. Double-check Start Command was saved correctly
2. Make sure it says `gevent` not `eventlet`
3. Try clearing cache again
4. Check if there's a `Procfile` that might override the command (delete it if exists)

---

## ⏱️ Timeline

- **Update Start Command:** 30 seconds
- **Save:** Instant
- **Clear cache & deploy:** 4-5 minutes
- **Test:** 30 seconds

**Total: ~6 minutes**

---

## 🎉 After This Fix

Everything will work perfectly:

- ✅ Python 3.11 (compatible)
- ✅ Gevent worker (no timeout)
- ✅ All endpoints work
- ✅ /my-orders works (no timeout!)
- ✅ Mobile app connects
- ✅ No more errors!

---

## 🚀 DO IT NOW!

### Quick Summary:

1. **Settings** → **Start Command** → Paste gevent command → **Save**
2. **Settings** → **Clear build cache & deploy** → **Confirm**
3. **Wait** 4-5 minutes
4. **Test** → **Success!** 🎉

---

**Status:** ⚠️ **URGENT** - Clear cache needed!

**Priority:** 🔴 **CRITICAL** - Old cache is blocking the fix!

**Time:** ⏱️ **6 minutes**

**Difficulty:** 🟢 **EASY** - Just 2 actions in Settings!

**Last Updated:** May 22, 2026

---

## 📸 Screenshot Guide

### 1. Start Command Location:
```
Settings → Build & Deploy → Start Command
[                                                    ]
[  gunicorn --worker-class gevent -w 1 --bind      ]
[  0.0.0.0:10000 wsgi:app                          ]
[                                                    ]
                                    [Save Changes]
```

### 2. Clear Cache Location:
```
Settings → Scroll Down → Build & Deploy

[Clear build cache & deploy]  ← CLICK THIS!
```

---

**READY? GO CLEAR THAT CACHE!** 🚀
