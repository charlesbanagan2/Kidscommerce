# FORGOT PASSWORD - TESTING GUIDE

## What I Fixed:

1. ✅ **Fixed Flutter animation error** in forgot_password_screen.dart
2. ✅ **Updated backend API endpoints** with proper email sending
3. ✅ **Added better error messages** for incorrect codes
4. ✅ **Added confirmation emails** after password reset

## Email Configuration:

Your app.py already has working email credentials hardcoded:
- MAIL_SENDER: ccody7313@gmail.com
- MAIL_APP_PASSWORD: ecjdfangradrblcl (App Password)

These will be used automatically since your .env has placeholders.

## How to Test:

### Step 1: Restart Your Backend
```bash
cd c:\Users\mnban\Documents\kids\backend
python app.py
```

### Step 2: Test from Mobile App
1. Open your Flutter app
2. Go to Login screen
3. Tap "Forgot Password?"
4. Enter: malakaslang53@gmail.com
5. Tap "Send Reset Code"

### Step 3: Check Email
- Check the Gmail inbox for malakaslang53@gmail.com
- You should receive an email with subject: "Kids Kingdom - Password Reset Code"
- The email will contain a 6-digit code

### Step 4: Reset Password
1. Enter the 6-digit code from email
2. Enter new password (must meet requirements):
   - 8-12 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 number
   - At least 1 special character (!@#$%^&*-_)
3. Confirm the password
4. Tap "Reset Password"

### Step 5: Test Login
- Go back to login screen
- Login with the new password

## Error Messages You'll See:

### Incorrect Code:
- First attempt: "❌ Invalid code. Please check your email and try again."
- Second attempt: "❌ Invalid code. Attempt 2 of 3. Double-check your email."
- Third+ attempt: "🚫 Too many failed attempts. Please request a new code."

### Code Expired:
- "⏰ Code has expired. Please request a new one."

### Connection Error:
- "📡 Connection error. Please check your internet and try again."

## Troubleshooting:

### If email is not received:

1. **Check spam folder** - Gmail might filter it

2. **Check backend logs** - Look for:
   ```
   Password reset code sent to malakaslang53@gmail.com
   ```
   Or error messages like:
   ```
   Failed to send reset email to malakaslang53@gmail.com: [error details]
   ```

3. **Test email manually**:
   ```bash
   cd c:\Users\mnban\Documents\kids\backend
   python test_email.py
   ```
   Enter: malakaslang53@gmail.com

4. **Check if user exists**:
   - Make sure malakaslang53@gmail.com is registered in your database
   - The API returns 404 if email is not found

### If you get "connection error" in app:

1. **Check backend is running** on http://192.168.1.20:5000
2. **Check your phone is on same WiFi** as your computer
3. **Test the endpoint manually**:
   ```bash
   curl -X POST http://192.168.1.20:5000/api/v1/auth/forgot-password \
     -H "Content-Type: application/json" \
     -d "{\"email\":\"malakaslang53@gmail.com\"}"
   ```

## API Endpoints:

### Forgot Password
```
POST /api/v1/auth/forgot-password
Body: {"email": "user@gmail.com"}
Response: {"success": true, "message": "Reset code sent to your email"}
```

### Reset Password
```
POST /api/v1/auth/reset-password
Body: {
  "email": "user@gmail.com",
  "code": "123456",
  "new_password": "NewPass123!"
}
Response: {"success": true, "message": "Password reset successfully"}
```

## Next Steps:

1. Restart your backend server
2. Test the forgot password flow
3. Check your email (malakaslang53@gmail.com)
4. If you don't receive email, check backend logs
5. Report any errors you see

## Notes:

- Reset codes are stored in the `verification_code` field of the user table
- Codes don't expire automatically (you can add expiration later if needed)
- The Flutter app already has attempt tracking (3 attempts max)
- Confirmation email is sent after successful password reset
