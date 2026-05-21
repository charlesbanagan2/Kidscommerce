# JWT_SECRET_KEY Lazy Loading Fix - COMPLETE ✅

## Problem

Server failed to start with error:
```
ValueError: JWT_SECRET_KEY environment variable is not set!
Please add JWT_SECRET_KEY to your .env file.
```

**Root Cause**: 
- `notification_api_endpoints.py` and `notification_chat_api.py` were trying to load `JWT_SECRET_KEY` at module import time
- This happened BEFORE `load_dotenv()` was called in `app.py`
- Result: `.env` file not loaded yet, so `JWT_SECRET_KEY` was `None`

---

## Solution

Changed JWT_SECRET_KEY loading from **eager** (at import time) to **lazy** (when first needed).

### Files Fixed:

1. **`backend/notification_api_endpoints.py`**
2. **`backend/notification_chat_api.py`**

---

## What Was Changed

### Before (Eager Loading - BROKEN):
```python
# JWT Secret - Load from environment (REQUIRED)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is not set! "
        "Please add JWT_SECRET_KEY to your .env file."
    )
```

**Problem**: This runs when the module is imported, BEFORE `.env` is loaded.

### After (Lazy Loading - FIXED):
```python
# JWT Secret - Will be loaded from environment when needed
_JWT_SECRET_KEY = None

def get_jwt_secret():
    """Get JWT_SECRET_KEY from environment (lazy loading)"""
    global _JWT_SECRET_KEY
    if _JWT_SECRET_KEY is None:
        _JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        if not _JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is not set! "
                "Please add JWT_SECRET_KEY to your .env file."
            )
    return _JWT_SECRET_KEY
```

**Solution**: Validation only happens when `get_jwt_secret()` is called (after `.env` is loaded).

### Updated Token Decoder:
```python
# Before:
payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

# After:
payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
```

---

## How It Works

### Import Order (Before Fix - BROKEN):
```
1. app.py starts
2. Imports notification_api_endpoints.py
3. notification_api_endpoints.py tries to load JWT_SECRET_KEY
4. ❌ ERROR: .env not loaded yet, JWT_SECRET_KEY is None
5. Server crashes
```

### Import Order (After Fix - WORKING):
```
1. app.py starts
2. Imports notification_api_endpoints.py
3. notification_api_endpoints.py defines get_jwt_secret() function (doesn't call it)
4. ✅ No error, module loads successfully
5. app.py calls load_dotenv()
6. .env file loaded, JWT_SECRET_KEY available
7. Later: When API endpoint is called, get_jwt_secret() is called
8. ✅ JWT_SECRET_KEY loaded successfully
```

---

## Files Modified

### 1. `backend/notification_api_endpoints.py`
**Changes**:
- Line ~24: Changed from eager loading to lazy loading
- Line ~73: Updated `jwt.decode()` to use `get_jwt_secret()`

**Before**:
```python
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError(...)

# Later in code:
payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
```

**After**:
```python
_JWT_SECRET_KEY = None

def get_jwt_secret():
    global _JWT_SECRET_KEY
    if _JWT_SECRET_KEY is None:
        _JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        if not _JWT_SECRET_KEY:
            raise ValueError(...)
    return _JWT_SECRET_KEY

# Later in code:
payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
```

### 2. `backend/notification_chat_api.py`
**Changes**:
- Line ~20: Changed from eager loading to lazy loading
- Line ~35: Updated `jwt.decode()` to use `get_jwt_secret()`

Same pattern as above.

---

## Test Results

### Before Fix:
```bash
$ python backend/app.py

Traceback (most recent call last):
  File "app.py", line 35, in <module>
    from notification_api_endpoints import register_notification_api
  File "notification_api_endpoints.py", line 26, in <module>
    raise ValueError(
ValueError: JWT_SECRET_KEY environment variable is not set!
Please add JWT_SECRET_KEY to your .env file.
```

### After Fix:
```bash
$ python backend/app.py

[OK] Product chat API registered
[OK] Notification API registered with optimizations
[OK] Notification API initialized
[OK] Google Login API initialized
[OK] Email Verification API initialized
[OK] Return & Refund API registered
[OK] ChatMessage model loaded
[OK] Unified chat system registered
[OK] Notification table columns verified
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.26:5000
Press CTRL+C to quit
```

✅ **Server starts successfully!**

---

## Why Lazy Loading?

### Benefits:
1. ✅ **Allows .env to load first** - Environment variables available when needed
2. ✅ **Maintains security** - Still validates JWT_SECRET_KEY is set
3. ✅ **Clear error messages** - If key missing, error shows when API is called
4. ✅ **No performance impact** - Key loaded once and cached

### Pattern:
```python
# Lazy loading pattern
_VARIABLE = None

def get_variable():
    global _VARIABLE
    if _VARIABLE is None:
        _VARIABLE = os.getenv('VARIABLE_NAME')
        if not _VARIABLE:
            raise ValueError("VARIABLE_NAME not set!")
    return _VARIABLE
```

This is a common pattern in Python for loading configuration that depends on environment setup.

---

## Other Files Checked

### ✅ `backend/unified_chat_api.py`
**Status**: Already uses lazy loading
```python
def get_user_from_token():
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        return None
    # ... use JWT_SECRET_KEY
```

No changes needed - already loads inside function.

### ✅ `backend/app.py`
**Status**: Loads JWT_SECRET_KEY after load_dotenv()
```python
load_dotenv()  # Load .env first
# ...
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Then load key
if not JWT_SECRET_KEY:
    raise ValueError(...)
```

No changes needed - correct order.

---

## Summary

### Problem:
- Server crashed on startup
- JWT_SECRET_KEY loaded before .env file

### Solution:
- Changed to lazy loading
- JWT_SECRET_KEY loaded when first needed
- Maintains security validation

### Result:
- ✅ Server starts successfully
- ✅ JWT authentication still works
- ✅ Security validation intact
- ✅ Clear error messages if key missing

---

## Summary (Tagalog)

### Problema:
- Server hindi nag-start
- Error: "JWT_SECRET_KEY environment variable is not set!"
- Dahilan: Nag-load ng JWT_SECRET_KEY bago pa ma-load ang .env file

### Solusyon:
- Changed to "lazy loading"
- JWT_SECRET_KEY na-load lang kapag kailangan na
- Security validation pa rin nandyan

### Resulta:
- ✅ Server nag-start ng maayos
- ✅ JWT authentication gumagana pa rin
- ✅ Security pa rin secure
- ✅ Clear error messages kung wala ang key

---

**Date**: May 21, 2026  
**Status**: ✅ FIXED  
**Server Status**: Running on http://192.168.1.26:5000  
**Files Modified**: 2 files
