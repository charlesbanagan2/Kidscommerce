# Render Deployment - Internal Server Error Fix

## Problem
Deployment succeeded but getting "Internal Server Error" when accessing https://kids-kingdom.onrender.com

## Root Cause
Environment variables are not configured in Render dashboard. The app needs:
- Database connection (SUPABASE_DB_URL)
- Email credentials (MAIL_SENDER, MAIL_APP_PASSWORD)
- API keys (SUPABASE_KEY, SUPABASE_SERVICE_KEY)
- Other configuration variables

## Solution: Configure Environment Variables in Render

### Step 1: Access Render Dashboard
1. Go to https://dashboard.render.com
2. Click on your "kids-kingdom" service
3. Click on "Environment" tab in the left sidebar

### Step 2: Add All Environment Variables

Copy these from your local `backend/.env` file and add them to Render:

#### Required Variables:

```bash
# ============================================
# GOOGLE OAUTH CREDENTIALS
# ============================================
GOOGLE_CLIENT_ID=43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co
SUPABASE_KEY=sb_publishable_PcSjw7T6f7D4tj3s8SxZKg_IqTuUhWM
SUPABASE_SERVICE_KEY=sb_secret_Kxo54KzgPd8haK3Za_-VkQ_AoTWJUhX
SUPABASE_DB_URL=postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres

# ============================================
# EMAIL CONFIGURATION (Gmail SMTP)
# ============================================
MAIL_SENDER=charlesgabrielle.banagan@lspu.edu.ph
MAIL_APP_PASSWORD=uadirdemyawgaemu
MAIL_SENDER_NAME=Kids Kingdom

# ============================================
# EMAIL VERIFICATION API
# ============================================
EMAILLISTVERIFY_API_KEY=WCoX3dgyRS7WsEVopg7afzNIfsQAfXVH

# ============================================
# FLASK CONFIGURATION
# ============================================
SECRET_KEY=KidsKingdom_SuperSecure_FlaskSession_Key_2026!#
JWT_SECRET_KEY=KidsKingdom_Mobile_Authentication_JWT_Secret_Token_072223
FLASK_ENV=production
DEBUG=False

# ============================================
# SERVER CONFIGURATION
# ============================================
HOST=0.0.0.0
PORT=10000

# ============================================
# CORS SETTINGS
# ============================================
ALLOWED_ORIGINS=https://kids-kingdom.onrender.com,http://localhost:3000
```

### Step 3: Important Notes

1. **Change FLASK_ENV to production:**
   ```
   FLASK_ENV=production
   DEBUG=False
   ```

2. **Update ALLOWED_ORIGINS:**
   ```
   ALLOWED_ORIGINS=https://kids-kingdom.onrender.com,http://localhost:3000
   ```

3. **PORT should be 10000** (Render's default)

### Step 4: Save and Redeploy

1. Click "Save Changes" button at the bottom
2. Render will automatically redeploy your service
3. Wait for deployment to complete (2-3 minutes)

## How to Add Environment Variables in Render

### Method 1: Through Dashboard (Recommended)
1. Go to your service → Environment tab
2. Click "Add Environment Variable"
3. Enter Key (e.g., `SUPABASE_URL`)
4. Enter Value (e.g., `https://qkdacoawexaxejljfihh.supabase.co`)
5. Click "Add"
6. Repeat for all variables
7. Click "Save Changes"

### Method 2: Bulk Add (Faster)
1. Click "Add from .env"
2. Paste all your environment variables
3. Click "Add Variables"
4. Review and save

## Checking Logs After Deployment

### View Real-time Logs:
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for errors like:
   - `KeyError: 'SUPABASE_URL'` → Missing environment variable
   - `Connection refused` → Database connection issue
   - `Authentication failed` → Wrong credentials

### Common Error Messages:

**Missing Environment Variable:**
```
KeyError: 'SUPABASE_URL'
```
**Fix:** Add the missing variable in Environment tab

**Database Connection Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Fix:** Check SUPABASE_DB_URL is correct

**Email Authentication Error:**
```
SMTPAuthenticationError: (535, 'Incorrect authentication data')
```
**Fix:** Verify MAIL_SENDER and MAIL_APP_PASSWORD

## Testing After Fix

### 1. Test Homepage:
```
https://kids-kingdom.onrender.com/
```
Should show: "Kids Kingdom API is running"

### 2. Test Health Check:
```
https://kids-kingdom.onrender.com/health
```
Should return: `{"status": "healthy"}`

### 3. Test API Endpoint:
```
https://kids-kingdom.onrender.com/api/products
```
Should return product list

### 4. Update Mobile App URL:
In `mobile_app/lib/config/url_config.dart`:
```dart
class UrlConfig {
  // Production URL (Render)
  static const String baseUrl = 'https://kids-kingdom.onrender.com';
  
  // ... rest of the code
}
```

## Troubleshooting

### If still getting 500 error after adding env vars:

1. **Check Render Logs:**
   - Look for specific error messages
   - Check if all imports are working
   - Verify database connection

2. **Verify Environment Variables:**
   - Go to Environment tab
   - Make sure all variables are saved
   - No typos in variable names

3. **Check Database Connection:**
   - Test Supabase connection from Render
   - Verify IP is not blocked
   - Check connection string format

4. **Restart Service:**
   - Go to Settings tab
   - Click "Manual Deploy" → "Clear build cache & deploy"

### Common Issues:

**Issue 1: Missing Dependencies**
```
ModuleNotFoundError: No module named 'flask'
```
**Fix:** Already fixed - requirements.txt is correct

**Issue 2: Port Binding**
```
Error: Failed to bind to 0.0.0.0:10000
```
**Fix:** Render automatically sets PORT=10000

**Issue 3: Database Migration**
```
sqlalchemy.exc.ProgrammingError: relation "user" does not exist
```
**Fix:** Run migrations (should auto-run on deploy)

## Quick Checklist

Before marking as complete, verify:

- [ ] All environment variables added to Render
- [ ] FLASK_ENV=production
- [ ] DEBUG=False
- [ ] ALLOWED_ORIGINS includes Render URL
- [ ] Service redeployed successfully
- [ ] Homepage loads without error
- [ ] API endpoints return data
- [ ] Mobile app can connect to production URL

## Next Steps

1. **Add environment variables to Render** (see Step 2 above)
2. **Save and wait for redeploy** (2-3 minutes)
3. **Check logs** for any errors
4. **Test the URL** - should work!
5. **Update mobile app** to use production URL

## Status: ⏳ WAITING FOR ENV VARS

Once you add the environment variables in Render dashboard, the internal server error will be fixed!
