# 🚨 How to Fix Render 500 Internal Server Error

## The Problem
Your app deployed successfully but shows "Internal Server Error" because **environment variables are missing**.

## The Solution (5 Minutes)

### Step 1: Open Render Dashboard
1. Go to: https://dashboard.render.com
2. Login with your account
3. Click on **"kids-kingdom"** service

### Step 2: Go to Environment Tab
1. Look at the left sidebar
2. Click on **"Environment"** tab
3. You'll see a list of environment variables (probably empty or incomplete)

### Step 3: Add Environment Variables

**Option A: Bulk Add (Fastest - Recommended)**
1. Click **"Add from .env"** button
2. Open the file: `RENDER_ENV_VARS.txt` (in your project root)
3. Copy ALL the content
4. Paste into Render
5. Click **"Add Variables"**
6. Click **"Save Changes"** at the bottom

**Option B: Add One by One**
1. Click **"Add Environment Variable"**
2. Add each variable:
   - Key: `SUPABASE_URL`
   - Value: `https://qkdacoawexaxejljfihh.supabase.co`
3. Repeat for all 16 variables (see RENDER_ENV_VARS.txt)
4. Click **"Save Changes"**

### Step 4: Wait for Redeploy
1. After saving, Render will automatically redeploy
2. Watch the **"Logs"** tab
3. Wait 2-3 minutes for deployment to complete
4. Look for: **"Your service is live 🎉"**

### Step 5: Test Your App
1. Open: https://kids-kingdom.onrender.com
2. Should see: **"Kids Kingdom API is running"** ✅
3. Test API: https://kids-kingdom.onrender.com/api/products
4. Should return product data ✅

## What Environment Variables Do

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Database connection URL |
| `SUPABASE_KEY` | Database API key |
| `SUPABASE_DB_URL` | Direct database connection |
| `MAIL_SENDER` | Email sending address |
| `MAIL_APP_PASSWORD` | Gmail app password |
| `SECRET_KEY` | Flask session security |
| `JWT_SECRET_KEY` | Mobile app authentication |
| `FLASK_ENV` | Production mode |
| `DEBUG` | Disable debug mode |
| `ALLOWED_ORIGINS` | CORS security |

## Quick Checklist

- [ ] Opened Render dashboard
- [ ] Clicked on "kids-kingdom" service
- [ ] Went to "Environment" tab
- [ ] Added all 16 environment variables
- [ ] Clicked "Save Changes"
- [ ] Waited for redeploy (2-3 min)
- [ ] Tested URL - works! ✅

## Troubleshooting

### Still getting 500 error?

1. **Check Logs Tab:**
   - Look for red error messages
   - Common: `KeyError: 'SUPABASE_URL'` means variable is missing

2. **Verify All Variables Added:**
   - Count should be 16 variables
   - No typos in variable names
   - Values copied correctly

3. **Force Redeploy:**
   - Go to "Manual Deploy" tab
   - Click "Clear build cache & deploy"
   - Wait for completion

### Need Help?

Check these files in your project:
- `RENDER_DEPLOYMENT_FIX.md` - Detailed guide
- `RENDER_ENV_VARS.txt` - All variables to copy
- `backend/.env` - Your local environment file

## After It Works

### Update Mobile App URL:
Edit `mobile_app/lib/config/url_config.dart`:
```dart
static const String baseUrl = 'https://kids-kingdom.onrender.com';
```

### Test Everything:
- ✅ Registration
- ✅ Login
- ✅ Product listing
- ✅ Orders
- ✅ Chat
- ✅ Email notifications

## Summary

**Problem:** Missing environment variables in Render
**Solution:** Add all 16 variables from RENDER_ENV_VARS.txt
**Time:** 5 minutes
**Result:** App works perfectly! 🎉

---

**Next:** Once working, update your mobile app to use the production URL!
