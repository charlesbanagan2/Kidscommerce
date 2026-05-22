# Registration 500 Error - Email Configuration Issue 🔧

## Problem
Registration returns **500 Internal Server Error** but user is created successfully in database. No confirmation email is sent.

**Symptoms:**
- ✅ User created in database
- ✅ Appears in admin pending approval
- ❌ Returns 500 error to mobile/web
- ❌ No confirmation email sent

## Root Cause
The email sending code is failing, likely due to:
1. **Missing environment variables** on Render.com (`MAIL_SENDER`, `MAIL_APP_PASSWORD`)
2. **Invalid Gmail App Password**
3. **Gmail security blocking** the login attempt

## Current Email Configuration
```python
app.config['MAIL_SENDER'] = os.getenv('MAIL_SENDER', 'gbanagan33@gmail.com')
app.config['MAIL_APP_PASSWORD'] = os.getenv('MAIL_APP_PASSWORD', 'hprhqjfxpdfahxsf')
```

## Fix Applied
The email sending is already wrapped in `try-except`, but we need to ensure Render.com has the correct environment variables.

## Solution Steps

### Step 1: Verify Environment Variables on Render.com

1. Go to https://dashboard.render.com/
2. Click on your service: **kids-kingdom**
3. Click **Environment** (left sidebar)
4. Check if these variables exist:
   - `MAIL_SENDER` = `gbanagan33@gmail.com`
   - `MAIL_APP_PASSWORD` = `hprhqjfxpdfahxsf`

### Step 2: Add Missing Environment Variables

If the variables are missing, add them:

1. Click **Add Environment Variable**
2. Add:
   ```
   Key: MAIL_SENDER
   Value: gbanagan33@gmail.com
   ```
3. Click **Add Environment Variable** again
4. Add:
   ```
   Key: MAIL_APP_PASSWORD
   Value: hprhqjfxpdfahxsf
   ```
5. Click **Save Changes**

### Step 3: Verify Gmail App Password

The Gmail App Password might be invalid or expired. To generate a new one:

1. Go to https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Enable **2-Step Verification** (if not enabled)
4. Scroll down to **App passwords**
5. Click **App passwords**
6. Select:
   - App: **Mail**
   - Device: **Other (Custom name)**
   - Name: **Kids Kingdom**
7. Click **Generate**
8. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
9. Remove spaces: `abcdefghijklmnop`
10. Update `MAIL_APP_PASSWORD` in Render.com with this new password

### Step 4: Restart Render.com Service

After updating environment variables:

1. Go to https://dashboard.render.com/
2. Click on your service: **kids-kingdom**
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait 3-4 minutes for deployment to complete

### Step 5: Test Registration

1. Open mobile app or website
2. Register a new account
3. Should now return **201 success** (not 500)
4. Should receive confirmation email
5. User should appear in admin pending approval

## Alternative: Disable Email Temporarily

If you want registration to work without email (temporary fix):

The code already handles email errors gracefully - it logs the error but doesn't fail the registration. The 500 error might be coming from something else.

## Debugging Steps

### Check Render.com Logs

1. Go to https://dashboard.render.com/
2. Click on your service: **kids-kingdom**
3. Click **Logs** (top right)
4. Look for errors related to:
   - `Failed to send registration confirmation email`
   - `SMTP authentication error`
   - `Connection refused`

### Common Error Messages

**Error:** `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`
**Solution:** Invalid Gmail App Password. Generate a new one (Step 3 above)

**Error:** `SMTPServerDisconnected: Connection unexpectedly closed`
**Solution:** Gmail is blocking the connection. Enable "Less secure app access" or use App Password

**Error:** `gaierror: [Errno -2] Name or service not known`
**Solution:** Network issue on Render.com. Try redeploying.

## Testing Email Locally

To test if email works locally:

```bash
cd backend
python
```

```python
import smtplib
from email.mime.text import MIMEText

sender = 'gbanagan33@gmail.com'
password = 'hprhqjfxpdfahxsf'  # Your app password
recipient = 'test@gmail.com'  # Your test email

msg = MIMEText('Test email from Kids Kingdom')
msg['Subject'] = 'Test Email'
msg['From'] = sender
msg['To'] = recipient

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Email failed: {e}')
```

## Expected Behavior After Fix

### Successful Registration Flow:
```
User submits registration
↓
Backend creates user (status: pending)
↓
Backend sends admin notification ✅
↓
Backend sends confirmation email to user ✅
↓
Backend returns 201 success ✅
↓
Mobile app shows "Pending Approval" screen ✅
↓
User receives email: "Welcome to Kids Kingdom! Registration Received" ✅
```

## Files Involved
- `backend/app.py` - Registration endpoint (line ~15867-16320)
- `backend/.env` - Local environment variables
- Render.com Environment Variables - Cloud configuration

## Status Checklist
- [ ] Environment variables added to Render.com
- [ ] Gmail App Password verified/regenerated
- [ ] Service redeployed on Render.com
- [ ] Registration tested (should return 201)
- [ ] Confirmation email received
- [ ] User appears in admin pending approval

## Next Steps

1. **Immediate:** Add environment variables to Render.com
2. **Verify:** Test registration after deployment
3. **Monitor:** Check Render.com logs for any email errors
4. **Optional:** Set up email monitoring/alerts

---

**Last Updated:** May 22, 2026  
**Status:** ⚠️ ACTION REQUIRED - Configure Render.com Environment Variables  
**Priority:** 🔴 Critical - Blocking user registration
