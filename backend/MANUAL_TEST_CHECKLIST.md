# ✅ Reset Password Error Handling - Manual Test Checklist

## 🎯 Test Environment Setup

**Before Testing:**
1. ✅ Flask backend is running (`python app.py`)
2. ✅ Flutter app is running (Full restart, not hot reload)
3. ✅ Test email exists in database: `test@gmail.com`
4. ✅ Gmail SMTP is configured correctly
5. ✅ Check Flask console for debug messages

---

## 📋 Test Scenarios

### **Test 1: Wrong Code - 1st Attempt** ❌

**Steps:**
1. Open Flutter app
2. Go to Login → Forgot Password
3. Enter email: `test@gmail.com`
4. Click "Send Reset Code"
5. Check email for code (e.g., `123456`)
6. Enter WRONG code: `111111`
7. Enter valid password: `NewPass123!`
8. Click "Reset Password"

**Expected Result:**
```
❌ Invalid verification code. 2 attempt(s) remaining.
```

**Visual Checks:**
- [ ] Red border on code field
- [ ] Error message displays clearly
- [ ] Code field clears automatically
- [ ] No animation assertion errors in console

**Backend Response (Check Flask logs):**
```json
{
  "success": false,
  "error": "Invalid code. 2 attempt(s) remaining.",
  "error_type": "invalid_code",
  "attempts": 1,
  "remaining_attempts": 2
}
```

**Flutter Console Output:**
```
🔍 Reset Password Response: {success: false, error: Invalid code. 2 attempt(s) remaining., error_type: invalid_code, attempts: 1, remaining_attempts: 2}
```

---

### **Test 2: Wrong Code - 2nd Attempt** ❌

**Steps:**
1. After Test 1 failure
2. Enter another WRONG code: `222222`
3. Click "Reset Password"

**Expected Result:**
```
❌ Invalid verification code. 1 attempt(s) remaining.
```

**Visual Checks:**
- [ ] Red border on code field
- [ ] Attempt counter updates
- [ ] Code field clears automatically

**Backend Response:**
```json
{
  "success": false,
  "error": "Invalid code. 1 attempt(s) remaining.",
  "error_type": "invalid_code",
  "attempts": 2,
  "remaining_attempts": 1
}
```

---

### **Test 3: Wrong Code - 3rd Attempt** 🚫

**Steps:**
1. After Test 2 failure
2. Enter another WRONG code: `333333`
3. Click "Reset Password"

**Expected Result:**
```
🚫 Too many failed attempts. Please request a new code.
```

**Visual Checks:**
- [ ] Red border on code field
- [ ] Clear message about too many attempts
- [ ] Code field clears automatically
- [ ] Must request new code to continue

**Backend Response:**
```json
{
  "success": false,
  "error": "Too many failed attempts. Please request a new code.",
  "error_type": "too_many_attempts"
}
```

---

### **Test 4: Correct Code** ✅

**Steps:**
1. Request NEW reset code (after Test 3)
2. Check email for code (e.g., `654321`)
3. Enter CORRECT code from email
4. Enter valid password: `NewPass123!`
5. Confirm password: `NewPass123!`
6. Click "Reset Password"

**Expected Result:**
```
✓ Password reset successful!
```

**Visual Checks:**
- [ ] Green success message
- [ ] Checkmark animation appears
- [ ] Auto-redirect to login after 2 seconds
- [ ] Can login with new password

**Backend Response:**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

### **Test 5: Expired Code** ⏰

**Steps:**
1. Request reset code
2. Wait 5+ minutes
3. Enter the old code
4. Click "Reset Password"

**Expected Result:**
```
⏰ Code has expired. Please request a new one.
```

**Visual Checks:**
- [ ] Red border on code field
- [ ] Clear expiration message
- [ ] Code field clears automatically

**Backend Response:**
```json
{
  "success": false,
  "error": "Code has expired. Please request a new one.",
  "error_type": "expired_code"
}
```

---

### **Test 6: No Internet Connection** 📡

**Steps:**
1. Turn off WiFi/Mobile data
2. Enter any code
3. Click "Reset Password"

**Expected Result:**
```
📡 Connection error. Please check your internet and try again.
```

**Visual Checks:**
- [ ] Orange/yellow warning message
- [ ] Different from "Invalid code" message
- [ ] Can retry when internet is back

**Flutter Console Output:**
```
Reset password error: [Connection error details]
```

---

### **Test 7: Server Down** 🔴

**Steps:**
1. Stop Flask backend server
2. Enter any code
3. Click "Reset Password"

**Expected Result:**
```
📡 Connection error. Please check your internet and try again.
```

**Visual Checks:**
- [ ] Connection error message (not "Invalid code")
- [ ] App doesn't crash
- [ ] Can retry when server is back

---

### **Test 8: Invalid Email** ❌

**Steps:**
1. Request reset code for non-existent email
2. Should fail at forgot password step

**Expected Result:**
```
No account found with this email address
```

---

### **Test 9: Password Validation** 🔒

**Steps:**
1. Enter correct code
2. Enter weak password: `abc123`
3. Click "Reset Password"

**Expected Result:**
```
Password validation errors appear
```

**Visual Checks:**
- [ ] Password requirements shown
- [ ] Red error text under password field
- [ ] Form doesn't submit

---

### **Test 10: Password Mismatch** 🔒

**Steps:**
1. Enter correct code
2. Enter password: `NewPass123!`
3. Confirm password: `DifferentPass123!`
4. Click "Reset Password"

**Expected Result:**
```
Passwords do not match
```

**Visual Checks:**
- [ ] Error under confirm password field
- [ ] Form doesn't submit

---

## 🔍 Debug Checklist

### **If showing "Connection error" for wrong code:**

1. **Check Flask Console:**
   ```
   Look for: POST /api/v1/auth/reset-password
   Status code should be: 400 (not 500)
   ```

2. **Check Flutter Console:**
   ```
   Look for: 🔍 Reset Password Response:
   Should show: error_type: invalid_code
   ```

3. **Verify Backend Changes:**
   ```bash
   # Check if auth_mobile_api.py has error_type field
   grep "error_type" backend/auth_mobile_api.py
   ```

4. **Restart Everything:**
   ```bash
   # Stop Flask (Ctrl+C)
   # Restart Flask
   python app.py
   
   # Stop Flutter (Shift+F5)
   # Full restart (F5)
   ```

---

## ✅ Success Criteria

All tests should show:
- ✅ Correct error messages for each scenario
- ✅ No "Connection error" for wrong codes
- ✅ Attempt counter works (1 of 3, 2 of 3, etc.)
- ✅ Visual feedback is clear (red borders, animations)
- ✅ No assertion errors in console
- ✅ Smooth user experience

---

## 📊 Test Results Template

```
Date: _______________
Tester: _______________

Test 1 (Wrong Code 1st): [ ] PASS [ ] FAIL
Test 2 (Wrong Code 2nd): [ ] PASS [ ] FAIL
Test 3 (Wrong Code 3rd): [ ] PASS [ ] FAIL
Test 4 (Correct Code):   [ ] PASS [ ] FAIL
Test 5 (Expired Code):   [ ] PASS [ ] FAIL
Test 6 (No Internet):    [ ] PASS [ ] FAIL
Test 7 (Server Down):    [ ] PASS [ ] FAIL
Test 8 (Invalid Email):  [ ] PASS [ ] FAIL
Test 9 (Weak Password):  [ ] PASS [ ] FAIL
Test 10 (Mismatch):      [ ] PASS [ ] FAIL

Overall: [ ] ALL PASS [ ] SOME FAIL

Notes:
_________________________________
_________________________________
_________________________________
```

---

**Last Updated:** May 14, 2026
**Status:** Ready for Testing
