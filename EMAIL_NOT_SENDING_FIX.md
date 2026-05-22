# Email Not Sending - Troubleshooting Guide 📧

## Current Status
- ✅ Registration works (user created in database)
- ✅ User appears in admin pending approval
- ❌ **No confirmation email sent to user**
- ❌ **No admin notification email sent**

## Why Email Isn't Sending

The email sending code is wrapped in `try-except`, so it fails silently without breaking registration. This is good for user experience but bad for debugging.

## Possible Causes

### 1. Gmail App Password Invalid
**Most Likely Cause:** The Gmail App Password in Render.com might be incorrect or expired.

**Current Password:** `hprhqjfxpdfahxsf`

**How to Fix:**
1. Go to https://myaccount.google.com/
2. Click **Security** → **2-Step Verification**
3. Scroll to **App passwords**
4. Click **App passwords**
5. Generate new password for "Mail" → "Other (Kids Kingdom)"
6. Copy the 16-character password (remove spaces)
7. Update `MAIL_APP_PASSWORD` in Render.com Environment Variables
8. Redeploy service

### 2. Gmail Account Locked/Suspended
Gmail might have blocked the account due to suspicious activity.

**How to Check:**
1. Try logging in to https://mail.google.com/ with `gbanagan33@gmail.com`
2. Check for security alerts
3. If locked, follow Gmail's recovery process

### 3. SMTP Connection Blocked
Render.com might be blocking outgoing SMTP connections on port 465.

**How to Test:**
Check Render.com logs for errors like:
- `SMTPAuthenticationError`
- `Connection refused`
- `Timeout`

### 4. Missing Environment Variables
Even though you added them, they might not have loaded properly.

**How to Verify:**
1. Go to Render Dashboard → Your Service → Environment
2. Confirm these exist:
   - `MAIL_SENDER` = `gbanagan33@gmail.com`
   - `MAIL_APP_PASSWORD` = `hprhqjfxpdfahxsf`
   - `MAIL_SENDER_NAME` = `Kids Kingdom`
3. If missing, add them and redeploy

## How to Check Render.com Logs

### Step 1: Open Render Dashboard
```
https://dashboard.render.com/
```

### Step 2: View Logs
1. Click your service: **kids-kingdom**
2. Click **Logs** (top right)
3. Look for errors related to email

### Step 3: Search for Email Errors
Look for these patterns in logs:
```
Failed to send registration confirmation email
SMTPAuthenticationError
Connection refused
Timeout
```

## Quick Test: Send Test Email

To test if email works on Render.com, add this test endpoint:

```python
@app.route('/test-email')
def test_email():
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText('Test email from Kids Kingdom')
        msg['Subject'] = 'Test Email'
        msg['From'] = app.config['MAIL_SENDER']
        msg['To'] = 'your-test-email@gmail.com'  # Change this
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
        
        return 'Email sent successfully!'
    except Exception as e:
        return f'Email failed: {str(e)}'
```

Then visit: `https://kids-kingdom.onrender.com/test-email`

## Alternative: Use SendGrid (Recommended)

Gmail SMTP is not reliable for production. Consider using SendGrid:

### Why SendGrid?
- ✅ More reliable than Gmail SMTP
- ✅ Better deliverability
- ✅ Free tier: 100 emails/day
- ✅ No app password needed
- ✅ Better logging and analytics

### How to Setup SendGrid

1. **Sign up:** https://signup.sendgrid.com/
2. **Get API Key:** Settings → API Keys → Create API Key
3. **Update code:**

```python
# Install: pip install sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_sendgrid(to_email, subject, html_content):
    message = Mail(
        from_email='gbanagan33@gmail.com',
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        return True
    except Exception as e:
        app.logger.error(f'SendGrid error: {e}')
        return False
```

4. **Add to Render.com:**
```
SENDGRID_API_KEY = your_api_key_here
```

## Temporary Workaround: Disable Email

If you want registration to work without email temporarily:

The code already handles this! Email sending is wrapped in `try-except`, so registration works even if email fails. Users just won't receive confirmation emails.

## Recommended Solution

### Option 1: Fix Gmail SMTP (Quick)
1. Generate new Gmail App Password
2. Update `MAIL_APP_PASSWORD` in Render.com
3. Redeploy
4. Test registration

### Option 2: Switch to SendGrid (Better)
1. Sign up for SendGrid
2. Get API key
3. Update code to use SendGrid
4. Deploy
5. More reliable for production

## Testing Checklist

After fixing:

- [ ] Check Render.com logs for email errors
- [ ] Register new test account
- [ ] Check if confirmation email received
- [ ] Check if admin notification email received
- [ ] Verify email content is correct
- [ ] Test with different email providers (Gmail, Yahoo, Outlook)

## Common Error Messages

### `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`
**Cause:** Invalid Gmail App Password  
**Fix:** Generate new App Password

### `SMTPServerDisconnected: Connection unexpectedly closed`
**Cause:** Gmail blocking connection  
**Fix:** Enable "Less secure app access" or use App Password

### `gaierror: [Errno -2] Name or service not known`
**Cause:** Network issue  
**Fix:** Check Render.com network settings

### `Timeout`
**Cause:** SMTP port blocked  
**Fix:** Try port 587 with STARTTLS instead of 465 with SSL

## Alternative SMTP Configuration

If port 465 doesn't work, try port 587:

```python
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
    smtp.send_message(msg)
```

## Next Steps

1. **Check Render.com logs** for email errors
2. **Generate new Gmail App Password** if needed
3. **Update environment variables** in Render.com
4. **Redeploy** service
5. **Test** registration again
6. **Consider switching to SendGrid** for production

---

**Last Updated:** May 22, 2026  
**Status:** ⚠️ Email Not Sending - Needs Investigation  
**Priority:** 🟡 Medium - Registration works but no email confirmation
