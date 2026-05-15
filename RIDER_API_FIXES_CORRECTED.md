# Rider API Fixes - CORRECTED

## Issues Fixed

### 1. `/api/v1/rider/accept-order` - 500 Error (3.597s)
**Error:** "The current Flask app is not registered with this 'SQLAlchemy' instance"

**Root Cause:** 
- The code was wrapping database operations in `with app.app_context():` when already inside a Flask request context
- This created a nested context issue causing SQLAlchemy to lose track of the app registration
- Missing null checks for rider object
- Missing detailed error logging

**Fix Applied:**
- **REMOVED** the `with app.app_context():` wrapper (not needed in request handlers)
- Added null check for rider object: `if not rider or rider.status != 'active':`
- Added proper error handling with traceback logging
- Fixed attribute access using `getattr(rider, 'profile_picture', None)` for safety
- Improved rollback handling in exception block

**File:** `backend/rider_mobile_only_api.py`

### 2. `/api/chat/unread-count` - SQLAlchemy Error
**Error:** "Error getting unread count: The current Flask app is not registered with this 'SQLAlchemy' instance"

**Root Cause:**
- Same issue - unnecessary `with app.app_context():` wrapper inside a request handler
- No error handling, causing 500 errors

**Fix Applied:**
- **REMOVED** the `with app.app_context():` wrapper
- Added try-except block with graceful fallback (returns 0 on error)
- Added error logging for debugging

**File:** `backend/app.py` (line ~7082)

## Key Learning

**IMPORTANT:** Flask request handlers (`@app.route`) already run within an application context. Adding `with app.app_context():` inside them creates a nested context that can cause SQLAlchemy to lose its app registration.

**When to use `app.app_context()`:**
- ✅ In background tasks, CLI commands, or scripts outside request context
- ✅ In scheduled jobs or Celery tasks
- ❌ Inside `@app.route` handlers (already have context)
- ❌ Inside `@token_required` decorated functions (already in request)

## Testing Recommendations

1. **Test Accept Order Endpoint:**
   ```bash
   curl -X POST http://192.168.1.20:5000/api/v1/rider/accept-order \
     -H "Authorization: Bearer <RIDER_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"order_id": 50}'
   ```

2. **Test Unread Count Endpoint:**
   ```bash
   curl -X GET http://192.168.1.20:5000/api/chat/unread-count \
     -H "Authorization: Bearer <TOKEN>"
   ```

3. **Monitor Server Logs:**
   - Check for "[SLOW]" messages (requests > 500ms)
   - Verify no more SQLAlchemy context errors
   - Confirm proper error logging with tracebacks

## Performance Notes

- The accept-order endpoint was taking 3.597s (SLOW)
- Removing the nested context should improve performance
- The row-level locking (`with_for_update()`) is correct for FCFS logic

## Files Modified

1. `backend/rider_mobile_only_api.py` - Fixed accept-order endpoint
2. `backend/app.py` - Fixed unread-count endpoint

## Deployment Steps

1. ✅ Backup current files
2. ✅ Apply the fixes (CORRECTED - removed app_context wrappers)
3. 🔄 Restart Flask server
4. 🧪 Test all rider endpoints
5. 📊 Monitor logs for any remaining issues

## Expected Behavior After Fix

- ✅ `/api/v1/rider/accept-order` should return 200 with order details
- ✅ `/api/chat/unread-count` should return 200 with count
- ✅ No more SQLAlchemy context errors in logs
- ✅ Improved response times (< 1s for accept-order)
