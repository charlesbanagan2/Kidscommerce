# 🚨 KAILANGAN GAWIN NGAYON! 🚨

## Problema

Ang deployment ay **FAILED** dahil mali ang command na ginagamit ng Render.

**Mali (current):**
```
gunicorn app:app  ❌
```

**Tama (dapat):**
```
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app  ✅
```

---

## ⚡ QUICK FIX - 3 Steps Lang!

### Step 1: Open Render Dashboard
```
https://dashboard.render.com/
```

### Step 2: Update Start Command

1. Click: **kids-ecommerce-api** (your service)
2. Click: **Settings** (left sidebar)
3. Scroll to: **Build & Deploy** section
4. Find: **Start Command** field
5. **REPLACE** with this EXACT command:

```
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

6. Click: **Save Changes** (blue button)

### Step 3: Redeploy

1. Click: **Manual Deploy** (top right)
2. Click: **Deploy latest commit**
3. Watch the logs

---

## ✅ Paano Malaman na Tama Na?

Sa logs, dapat makita mo:

```
✅ Starting service with 'gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app'
✅ Using worker: eventlet
✅ Booting worker with pid: XXXX
✅ Listening at: http://0.0.0.0:10000
```

**HINDI dapat:**
```
❌ Running 'gunicorn app:app'
```

---

## 🧪 Test After Deployment

Pag nag-"Live" na, i-test:

1. https://kidscommerce-backend.onrender.com/
2. https://kidscommerce-backend.onrender.com/api/health
3. https://kidscommerce-backend.onrender.com/api/products

**Expected:** Data (NOT 404!)

---

## 📸 Screenshot Guide

### Where to Find Start Command:

```
Render Dashboard
  └─ kids-ecommerce-api
      └─ Settings (left sidebar)
          └─ Build & Deploy section
              └─ Start Command field  ← EDIT THIS!
```

### What to Type:

```
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
```

**COPY-PASTE** yan para walang typo!

---

## ⏱️ Timeline

- Update command: **30 seconds**
- Save: **Instant**
- Redeploy: **3-4 minutes**
- **Total: ~5 minutes**

---

## 🆘 Kung May Problema

### Problem: Can't find Start Command field

**Solution:** 
- Make sure you're in **Settings** tab
- Scroll down to **Build & Deploy**
- Look for "Start Command" or "Run Command"

### Problem: Save button is disabled

**Solution:**
- Make sure you actually changed the text
- Try refreshing the page
- Try a different browser

### Problem: Still getting 404 after redeploy

**Solution:**
- Check logs - verify correct command is used
- Make sure you clicked "Save Changes"
- Try clearing the field completely, then paste again

---

## 🎯 DO THIS NOW!

1. **Open:** https://dashboard.render.com/
2. **Go to:** kids-ecommerce-api → Settings
3. **Update:** Start Command
4. **Save** and **Redeploy**
5. **Wait** 3-4 minutes
6. **Test** the URLs

**Yan lang! Simple fix sa dashboard lang!** 🚀

---

**Need Help?**
- Read: `RENDER_DASHBOARD_FIX.md` for detailed instructions
- Check: Render logs for error messages
- Verify: Start command in Settings matches exactly

**Last Updated:** May 22, 2026  
**Status:** ⚠️ ACTION REQUIRED - Update Render Dashboard
