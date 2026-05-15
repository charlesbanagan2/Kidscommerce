# 📧 Gmail SMTP Setup Guide - Kids Kingdom

## ❌ Current Problem

```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Bakit nangyayari ito?**
- Gmail no longer accepts regular passwords for SMTP
- Kailangan ng **App Password** (16-character special password)
- Security feature ng Google para sa third-party apps

---

## ✅ Solution: Setup Gmail App Password

### **Step 1: Enable 2-Factor Authentication** 🔐

1. Go to: **https://myaccount.google.com/security**
2. Scroll down to **"2-Step Verification"**
3. Click **"Get Started"**
4. Follow the steps:
   - Enter your password
   - Add your phone number
   - Verify with SMS code
   - Turn on 2-Step Verification

**Note:** Kailangan muna ng 2FA bago makagawa ng App Password

---

### **Step 2: Generate App Password** 🔑

1. Go to: **https://myaccount.google.com/apppasswords**
   - Or search "App Passwords" sa Google Account settings

2. You might need to sign in again

3. Under "Select app":
   - Choose **"Mail"**

4. Under "Select device":
   - Choose **"Other (Custom name)"**
   - Type: **"Kids Kingdom App"**

5. Click **"Generate"**

6. **IMPORTANT:** Copy the 16-character password
   - Format: `xxxx xxxx xxxx xxxx` (with spaces)
   - Example: `abcd efgh ijkl mnop`
   - **Save this password!** Hindi mo na ito makikita ulit

---

### **Step 3: Update Configuration File** ⚙️

1. Open file: `mobile_app/lib/kids_commercedb/supabase.env`

2. Add or update these lines at the bottom:

```env
# Gmail SMTP Configuration
MAIL_SENDER=gbanagan33@gmail.com
MAIL_APP_PASSWORD=abcdefghijklmnop
MAIL_SENDER_NAME=Kids Kingdom
```

**IMPORTANT:** 
- Remove spaces from the App Password
- If generated password is: `abcd efgh ijkl mnop`
- Use: `abcdefghijklmnop` (no spaces)

---

### **Step 4: Test the Configuration** 🧪

1. Open terminal/command prompt

2. Navigate to backend folder:
```bash
cd C:\Users\mnban\OneDrive\Desktop\kids\backend
```

3. Run the test script:
```bash
python test_email.py
```

4. Enter your test email address (or press Enter to use sender email)

5. Check your inbox for the test email

**Expected Result:**
```
✅ SUCCESS! Test email sent successfully!
📬 Check your inbox at: your-email@gmail.com

🎉 Your Gmail SMTP configuration is working!
```

---

### **Step 5: Restart Your Application** 🔄

1. Stop your Flask server (Ctrl+C)

2. Start it again:
```bash
python app.py
```

3. Test forgot password feature:
   - Go to login page
   - Click "Forgot Password"
   - Enter email
   - Check inbox for verification code

---

## 📧 Email Templates Now Available

After setup, these professional emails will work:

### 1. **Password Reset Code** 🔐
- Beautiful gradient purple design
- Large verification code display
- 5-minute expiration warning
- Security tips

### 2. **Account Approved** 🎉
- Congratulations message
- List of features available
- Login button
- Welcome message

### 3. **Account Rejected** 📋
- Professional rejection notice
- Clear reason display
- Next steps guidance
- Contact support button

---

## 🔧 Troubleshooting

### Problem: "App Passwords option not showing"
**Solution:** 
- Make sure 2-Factor Authentication is enabled first
- Wait 5-10 minutes after enabling 2FA
- Try accessing directly: https://myaccount.google.com/apppasswords

### Problem: "Still getting authentication error"
**Solution:**
- Double-check the App Password (no spaces)
- Make sure you're using the correct Gmail address
- Verify the .env file is saved properly
- Restart the Flask application

### Problem: "Test email not received"
**Solution:**
- Check spam/junk folder
- Wait 1-2 minutes (may delay)
- Verify internet connection
- Try sending to a different email

---

## 📝 Current Configuration

**File:** `mobile_app/lib/kids_commercedb/supabase.env`

```env
# Current Gmail Account
MAIL_SENDER=gbanagan33@gmail.com

# Old password (NOT WORKING)
MAIL_APP_PASSWORD=hprhqjfxpdfahxsf

# Replace with your new 16-character App Password
MAIL_APP_PASSWORD=YOUR_NEW_APP_PASSWORD_HERE
```

---

## ✅ Checklist

- [ ] Enable 2-Factor Authentication on Gmail
- [ ] Generate App Password
- [ ] Copy 16-character password (remove spaces)
- [ ] Update supabase.env file
- [ ] Run test_email.py script
- [ ] Verify test email received
- [ ] Restart Flask application
- [ ] Test forgot password feature
- [ ] Test account approval email
- [ ] Test account rejection email

---

## 🎯 Next Steps After Setup

1. **Test all email features:**
   - Forgot password
   - Account approval
   - Account rejection
   - Coupon emails

2. **Update email content:**
   - Replace `http://localhost:5000` with your actual domain
   - Update phone number: `+63 XXX XXX XXXX`
   - Update support email if different

3. **Monitor email delivery:**
   - Check Flask logs for errors
   - Monitor Gmail sending limits (500 emails/day)
   - Consider upgrading to professional email service for production

---

## 📞 Need Help?

If you encounter any issues:

1. Check Flask logs for detailed error messages
2. Run `python test_email.py` to diagnose
3. Verify all steps in this guide
4. Make sure 2FA is enabled on Gmail account

---

**Last Updated:** May 14, 2026
**Version:** 1.0
**Status:** Ready for Implementation
