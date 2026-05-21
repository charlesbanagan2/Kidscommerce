# 🚀 Environment Variables Quick Reference

## 📦 What Was Created

1. ✅ **`backend/.env`** - Your actual credentials (DO NOT COMMIT)
2. ✅ **`backend/.env.example`** - Template for documentation (safe to commit)
3. ✅ **`backend/env_loader_boilerplate.py`** - Code examples
4. ✅ **`GOOGLE_OAUTH_SUPABASE_SETUP.md`** - Complete setup guide

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Package
```bash
pip install python-dotenv
```

### Step 2: Add to Top of `app.py`
```python
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env', override=True)

# Get credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
```

### Step 3: Use in Your Code
```python
# Google OAuth
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["openid", "email", "profile"]
)

# Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flask
app.config['SECRET_KEY'] = SECRET_KEY
```

---

## 🔑 Your Credentials

### Google OAuth
```
Client ID: 43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com
Secret: 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
```

### Supabase
```
URL: https://qkdacoawexaxejljfihh.supabase.co
```

### ⚠️ Still Need:
- Supabase Anon Key (from Supabase Dashboard → Settings → API)
- Supabase Service Key (from same location)
- Flask Secret Key (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

---

## 🔒 Security Checklist

- [ ] `.env` file created in `backend/` folder
- [ ] `.env` added to `.gitignore`
- [ ] `python-dotenv` installed
- [ ] Code updated to use `os.getenv()`
- [ ] No hardcoded credentials in code
- [ ] Server tested and working

---

## 🐛 Common Issues

### "Module 'dotenv' not found"
```bash
pip install python-dotenv
```

### "Variables are None"
- Check `.env` file exists in correct location
- Verify `load_dotenv()` is called before `os.getenv()`
- No spaces around `=` in `.env` file

### "Google OAuth fails"
- Add redirect URI in Google Console: `http://192.168.1.26:5000/login/google/authorized`
- Check credentials are correct in `.env`

---

## 📖 Full Documentation

See `GOOGLE_OAUTH_SUPABASE_SETUP.md` for complete guide with:
- Detailed explanations
- Troubleshooting
- Security best practices
- Testing instructions

---

## 🎯 Current URLs

### Mobile App
```dart
// mobile_app/lib/config/url_config.dart
static const String _wifiHost = '192.168.1.26';
static const int backendPort = 5000;
```

### Backend
```python
# backend/app.py (at bottom)
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### Access Points
- **Backend API:** `http://192.168.1.26:5000`
- **Mobile App:** Connects to `192.168.1.26:5000`
- **Google OAuth Redirect:** `http://192.168.1.26:5000/login/google/authorized`

---

**Status:** ✅ Ready to implement
**Next:** Update `app.py` with environment loader code
