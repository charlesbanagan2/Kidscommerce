# 📧 Email Verification API Setup

## Overview
Your app uses **EmailListVerify API** for real-time email validation during registration and password reset.

---

## 🔑 API Configuration

### Added to `.env`:
```env
EMAILLISTVERIFY_API_KEY="your_emaillistverify_api_key_here"
```

### How to Get API Key:

1. **Visit:** https://emaillistverify.com/
2. **Sign up** for a free account
3. **Get API Key** from dashboard
4. **Copy** the API key
5. **Paste** into `.env` file

---

## 🔧 How It Works

### 1. **With API Key (Recommended)**
```python
# Real-time verification using EmailListVerify API
verifier = EmailVerifier(api_key='your_key')
result = verifier.verify_email('test@example.com')

# Returns:
{
    'valid': True,
    'reason': 'Valid email',
    'score': 100,
    'result': 'success',
    'api_used': True
}
```

### 2. **Without API Key (Fallback)**
```python
# Basic regex validation + disposable email check
result = verifier.verify_email('test@example.com')

# Returns:
{
    'valid': True,
    'reason': 'Valid',
    'score': 100,
    'result': 'success',
    'api_used': False  # Using fallback
}
```

---

## 📡 API Endpoints

### 1. Verify Single Email
```http
POST /api/verify-email
Content-Type: application/json

{
    "email": "test@example.com"
}
```

**Response:**
```json
{
    "valid": true,
    "reason": "Valid email",
    "score": 100,
    "api_used": true
}
```

### 2. Verify Multiple Emails (Batch)
```http
POST /api/verify-emails
Content-Type: application/json

{
    "emails": [
        "test1@example.com",
        "test2@example.com"
    ]
}
```

**Response:**
```json
{
    "test1@example.com": {
        "valid": true,
        "reason": "Valid email",
        "score": 100
    },
    "test2@example.com": {
        "valid": false,
        "reason": "Invalid email",
        "score": 0
    }
}
```

### 3. Check Verification Status
```http
GET /api/verify-email-status
```

**Response:**
```json
{
    "enabled": true,
    "api": "emaillistverify",
    "fallback_validation": "enabled"
}
```

---

## 🎯 Features

### ✅ Real-time Validation
- Checks if email exists
- Validates domain
- Detects typos
- Identifies disposable emails

### ✅ Fallback System
- Works without API key
- Basic regex validation
- Disposable email detection
- No service interruption

### ✅ Batch Processing
- Verify multiple emails
- Efficient for bulk operations
- Rate limit aware

---

## 🔍 Validation Results

### Result Types:
| Result | Meaning | Score |
|--------|---------|-------|
| `success` | Valid, deliverable email | 100 |
| `invalid` | Invalid or non-existent | 0 |
| `unknown` | Cannot verify (temporary) | 50 |

### Common Reasons:
- ✅ "Valid email" - Email is good
- ❌ "Invalid format" - Syntax error
- ❌ "Disposable email" - Temporary email service
- ❌ "Domain not found" - Invalid domain
- ⚠️ "Mailbox full" - Exists but full
- ⚠️ "Temporary error" - Try again later

---

## 🛡️ Disposable Email Detection

### Built-in Blocked Domains:
```python
disposable_domains = {
    'tempmail.com',
    'guerrillamail.com',
    '10minutemail.com',
    'mailinator.com',
    'temp-mail.org',
    'throwaway.email'
}
```

### In app.py:
```python
DISPOSABLE_DOMAINS = set([
    'mailinator.com',
    'yopmail.com',
    'guerrillamail.com',
    '10minutemail.com',
    'getnada.com',
    'tempmail.com',
    # ... more domains
])
```

---

## 💻 Usage in Your App

### During Registration:
```python
from email_verification import verify_email_address

# Verify email before creating account
is_valid, reason = verify_email_address(email)

if not is_valid:
    flash(f'Invalid email: {reason}', 'error')
    return redirect(url_for('register'))

# Proceed with registration
```

### During Password Reset:
```python
# Verify email exists and is valid
result = verifier.verify_email(email)

if not result['valid']:
    flash('Email address is invalid', 'error')
    return redirect(url_for('forgot_password'))

# Send reset code
```

---

## 🧪 Testing

### Test with Python:
```python
from email_verification import get_email_verifier

verifier = get_email_verifier()

# Test valid email
result = verifier.verify_email('test@gmail.com')
print(result)

# Test invalid email
result = verifier.verify_email('invalid@fake-domain-xyz.com')
print(result)

# Test disposable email
result = verifier.verify_email('test@tempmail.com')
print(result)
```

### Test API Endpoints:
```bash
# Test single email
curl -X POST http://192.168.1.26:5000/api/verify-email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com"}'

# Check status
curl http://192.168.1.26:5000/api/verify-email-status
```

---

## ⚙️ Configuration in app.py

### Initialization:
```python
from email_verification_api import register_email_verification_endpoints

# Register endpoints
try:
    register_email_verification_endpoints(app)
    print("[OK] Email Verification API initialized")
except Exception as e:
    print(f"[ERROR] Email Verification API failed: {e}")
```

### Environment Variable Loading:
```python
# In email_verification.py
self.api_key = api_key or os.getenv('EMAILLISTVERIFY_API_KEY', '').strip()
self.enabled = bool(self.api_key)
```

---

## 📊 API Limits

### EmailListVerify Free Tier:
- **100 verifications/month** (free)
- **Rate limit:** ~10 requests/minute
- **Response time:** < 1 second

### Paid Plans:
- More verifications
- Higher rate limits
- Priority support

### Fallback Behavior:
- If API fails → Uses basic validation
- If rate limit hit → Uses basic validation
- No service interruption

---

## 🔒 Security Features

### ✅ Prevents:
1. Fake email registrations
2. Disposable email abuse
3. Typo errors
4. Non-existent domains
5. Spam accounts

### ✅ Validates:
1. Email syntax
2. Domain existence
3. MX records
4. Mailbox existence
5. Deliverability

---

## 🐛 Troubleshooting

### "Email validation disabled"
**Cause:** API key not set
**Solution:** Add `EMAILLISTVERIFY_API_KEY` to `.env`

### "API error" in logs
**Cause:** Invalid API key or network issue
**Solution:** 
- Check API key is correct
- Verify internet connection
- Check EmailListVerify service status

### All emails marked invalid
**Cause:** API quota exceeded
**Solution:**
- Check your EmailListVerify dashboard
- Upgrade plan if needed
- Fallback validation will still work

### Slow verification
**Cause:** API timeout or network latency
**Solution:**
- Increase timeout in code
- Use batch verification for multiple emails
- Consider caching results

---

## 📝 Environment Variables Summary

```env
# Email Sending (Gmail SMTP)
MAIL_SENDER="gbanagan33@gmail.com"
MAIL_APP_PASSWORD="hprhqjfxpdfahxsf"
MAIL_SENDER_NAME="Kids Kingdom"

# Email Verification (EmailListVerify API)
EMAILLISTVERIFY_API_KEY="your_api_key_here"
```

---

## ✅ Setup Checklist

- [x] Email verification API added to `.env`
- [x] `EMAILLISTVERIFY_API_KEY` variable created
- [ ] Get API key from EmailListVerify.com
- [ ] Add API key to `.env` file
- [ ] Test email verification endpoint
- [ ] Verify fallback validation works
- [ ] Test with valid email
- [ ] Test with invalid email
- [ ] Test with disposable email

---

## 🎯 Next Steps

1. **Get API Key:**
   - Visit https://emaillistverify.com/
   - Sign up for free account
   - Copy API key

2. **Update `.env`:**
   ```env
   EMAILLISTVERIFY_API_KEY="your_actual_api_key_here"
   ```

3. **Test:**
   ```bash
   curl -X POST http://192.168.1.26:5000/api/verify-email \
     -H "Content-Type: application/json" \
     -d '{"email":"test@gmail.com"}'
   ```

4. **Monitor:**
   - Check logs for verification results
   - Monitor API usage in dashboard
   - Watch for rate limit warnings

---

**Status:** ✅ Configuration Added
**API:** EmailListVerify
**Fallback:** Basic validation enabled
**Endpoints:** 3 endpoints registered
