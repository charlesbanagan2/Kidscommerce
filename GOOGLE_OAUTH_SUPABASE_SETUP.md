# 🔐 Google OAuth & Supabase Environment Setup Guide

## Overview
This guide shows you how to securely configure Google OAuth and Supabase credentials in your Python Flask backend using environment variables.

---

## 📋 Prerequisites

### 1. Install Required Package
```bash
pip install python-dotenv
```

### 2. Verify Installation
```bash
pip list | grep python-dotenv
```

---

## 🔧 Step 1: Create `.env` File

**Location:** `backend/.env`

The `.env` file has been created with your credentials:
- ✅ Google Client ID: `43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com`
- ✅ Google Client Secret: `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`
- ✅ Supabase URL: `https://qkdacoawexaxejljfihh.supabase.co`

**⚠️ Important:** Update the following placeholders in `.env`:
- `SUPABASE_KEY` - Your Supabase anon/public key
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key (for admin operations)
- `SECRET_KEY` - Generate a secure random key for Flask sessions

---

## 🔒 Step 2: Secure Your `.env` File

### Add to `.gitignore`
```bash
# In your .gitignore file
.env
.env.*
!.env.example
```

### Verify it's ignored
```bash
git status
# .env should NOT appear in the list
```

---

## 💻 Step 3: Update Your `app.py`

### Add at the TOP of `app.py` (after imports):

```python
import os
from dotenv import load_dotenv
from pathlib import Path

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

# Get the directory where app.py is located
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / '.env', override=True)

# ============================================
# GOOGLE OAUTH CONFIGURATION
# ============================================

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("❌ Google OAuth credentials not found in .env file")

print(f"✅ Google OAuth loaded: {GOOGLE_CLIENT_ID[:20]}...")

# ============================================
# SUPABASE CONFIGURATION
# ============================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL:
    raise ValueError("❌ Supabase URL not found in .env file")

print(f"✅ Supabase configured: {SUPABASE_URL}")

# ============================================
# FLASK SETTINGS
# ============================================

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
```

---

## 🔄 Step 4: Update Google OAuth Blueprint

### Find your existing Google OAuth setup and replace with:

```python
from flask_dance.contrib.google import make_google_blueprint

# Create Google OAuth blueprint using environment variables
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="google_login_callback",
    redirect_url="/login/google/authorized"
)

app.register_blueprint(google_bp, url_prefix="/login")
```

---

## 🗄️ Step 5: Update Supabase Client

### Replace hardcoded Supabase initialization:

```python
from supabase import create_client, Client

# Initialize Supabase client using environment variables
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(f"✅ Supabase client initialized for: {SUPABASE_URL}")
```

---

## 🚀 Step 6: Update Flask App Configuration

```python
# Flask app configuration
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Run the server
if __name__ == "__main__":
    socketio.run(
        app, 
        host=HOST, 
        port=PORT, 
        debug=DEBUG, 
        allow_unsafe_werkzeug=True
    )
```

---

## ✅ Step 7: Test Your Setup

### 1. Start the server
```bash
cd backend
python app.py
```

### 2. Check console output
You should see:
```
✅ Google OAuth loaded: 43948051603-4urea9...
✅ Supabase configured: https://qkdacoawexaxejljfihh.supabase.co
✅ Supabase client initialized for: https://qkdacoawexaxejljfihh.supabase.co
```

### 3. Test Google Login
- Navigate to: `http://192.168.1.26:5000/login/google`
- Should redirect to Google OAuth consent screen
- After authorization, should redirect back to your app

---

## 🔍 How It Works

### 1. **Loading Process**
```
.env file → python-dotenv → os.getenv() → Your variables
```

### 2. **Execution Flow**
1. `load_dotenv()` reads the `.env` file
2. Parses key-value pairs
3. Sets them as environment variables
4. `os.getenv()` retrieves them
5. Variables are available throughout your app

### 3. **Security Benefits**
- ✅ Credentials never in source code
- ✅ Different values per environment
- ✅ Easy to rotate credentials
- ✅ No accidental commits to Git
- ✅ Team members use their own `.env`

---

## 🛠️ Troubleshooting

### Issue: "Google OAuth credentials not found"
**Solution:** 
- Check `.env` file exists in `backend/` folder
- Verify no typos in variable names
- Ensure no quotes around values in `.env`

### Issue: "Module 'dotenv' not found"
**Solution:**
```bash
pip install python-dotenv
```

### Issue: Variables are `None`
**Solution:**
- Check `.env` file path is correct
- Verify `load_dotenv()` is called before `os.getenv()`
- Check for spaces around `=` in `.env` (should be `KEY=value`)

### Issue: Google OAuth redirect fails
**Solution:**
- Verify redirect URIs in Google Cloud Console match your app
- Add: `http://192.168.1.26:5000/login/google/authorized`
- Add: `http://localhost:5000/login/google/authorized`

---

## 📝 Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `43948051603-xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | `GOCSPX-xxxxx` |
| `SUPABASE_URL` | Supabase Project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon Key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SECRET_KEY` | Flask Session Secret | Random string (32+ chars) |
| `DEBUG` | Enable Debug Mode | `True` or `False` |
| `HOST` | Server Host | `0.0.0.0` (all interfaces) |
| `PORT` | Server Port | `5000` |

---

## 🔐 Security Best Practices

### ✅ DO:
1. Keep `.env` in `.gitignore`
2. Use different `.env` for dev/prod
3. Rotate credentials regularly
4. Use strong `SECRET_KEY` (32+ random chars)
5. Validate all required variables on startup
6. Use `.env.example` for documentation

### ❌ DON'T:
1. Commit `.env` to Git
2. Share `.env` via email/chat
3. Use production credentials in development
4. Hardcode credentials in code
5. Log sensitive environment variables
6. Use weak or default secret keys

---

## 📚 Additional Resources

- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [Google OAuth Setup Guide](https://developers.google.com/identity/protocols/oauth2)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Flask Configuration](https://flask.palletsprojects.com/en/2.3.x/config/)

---

## ✅ Checklist

- [ ] `.env` file created in `backend/` folder
- [ ] `python-dotenv` installed
- [ ] `.env` added to `.gitignore`
- [ ] Environment loader code added to `app.py`
- [ ] Google OAuth blueprint updated
- [ ] Supabase client updated
- [ ] Flask config updated
- [ ] Server tested and running
- [ ] Google login tested
- [ ] Supabase connection tested

---

**Status:** ✅ Ready to implement
**Date:** May 21, 2026
**Files Created:**
- `backend/.env`
- `backend/env_loader_boilerplate.py`
- `GOOGLE_OAUTH_SUPABASE_SETUP.md`
