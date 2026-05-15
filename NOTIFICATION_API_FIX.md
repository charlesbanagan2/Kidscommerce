# Notification API SQLAlchemy Context Fix

## Problem
The notification API endpoints were returning 500 errors with:
```
RuntimeError: The current Flask app is not registered with this 'SQLAlchemy' instance
```

## Root Cause
The `_db` global variable in `notification_api_endpoints.py` was being used directly in blueprint endpoints without proper Flask app context binding. When a blueprint executes, it needs to access the database through the current Flask app context, not through a global reference that may not be bound to the active app.

## Solution
Changed all database access in the blueprint endpoints to use a local `db` variable that's assigned from the global `_db` at the start of each endpoint function. This ensures:

1. **Proper Context Binding**: Each endpoint gets a fresh reference to the database instance
2. **Consistent Access Pattern**: All endpoints use `db.session.query()` instead of `_db.session.query()`
3. **Error Handling**: Added checks to ensure `_db` is not None before using it

## Changes Made

### File: `notification_api_endpoints.py`

#### 1. Updated `get_db()` function
```python
def get_db():
    """Get database instance from current Flask app context"""
    global _db
    if _db is not None:
        return _db
    # Fallback: try to get from current app
    try:
        from flask import current_app
        if 'sqlalchemy' in current_app.extensions:
            return current_app.extensions['sqlalchemy']
    except:
        pass
    return _db
```

#### 2. Updated all endpoint functions
Each endpoint now:
- Checks if `_db` is None and returns error if not initialized
- Assigns `db = _db` at the start
- Uses `db.session.query()` instead of `_db.session.query()`
- Uses `db.session.commit()` instead of `_db.session.commit()`
- Uses `db.session.rollback()` instead of `_db.session.rollback()`

**Affected endpoints:**
- `GET /api/v1/notifications` - get_notifications()
- `GET /api/v1/notifications/unread-count` - get_unread_count()
- `PUT /api/v1/notifications/<id>/read` - mark_notification_read()
- `PUT /api/v1/notifications/mark-all-read` - mark_all_read()
- `DELETE /api/v1/notifications/<id>` - delete_notification()
- `DELETE /api/v1/notifications/clear-all` - clear_all_read()
- `GET/PUT /api/v1/notifications/settings` - notification_settings()
- `POST /api/v1/admin/notifications/broadcast` - broadcast_notification()

#### 3. Example of the fix
**Before:**
```python
def get_unread_count(current_user_id, current_user_role):
    if _Notification is None:
        return jsonify({'success': False, 'message': 'Not initialized'}), 500
    
    Notification = _Notification
    
    try:
        unread_count = _db.session.query(Notification).filter_by(
            user_id=current_user_id,
            is_read=False
        ).count() or 0
```

**After:**
```python
def get_unread_count(current_user_id, current_user_role):
    if _Notification is None or _db is None:
        return jsonify({'success': False, 'message': 'Not initialized'}), 500
    
    Notification = _Notification
    db = _db  # Local reference
    
    try:
        unread_count = db.session.query(Notification).filter_by(
            user_id=current_user_id,
            is_read=False
        ).count() or 0
```

## Testing
After applying these changes:

1. **Restart the Flask server**
2. **Test the notification endpoints:**
   ```bash
   # Get notifications
   curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/notifications
   
   # Get unread count
   curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/notifications/unread-count
   ```

3. **Expected Result**: 200 OK responses with notification data instead of 500 errors

## Why This Works
- The `_db` global is set during `register_notification_api()` which is called after models are defined
- Each endpoint creates a local `db` variable from the global `_db`
- This local reference is used consistently throughout the endpoint
- The Flask app context is properly maintained because we're using the same `db` instance that was initialized with the app

## Files Modified
- `backend/notification_api_endpoints.py` - All 8 endpoints updated

## Deployment Notes
- No database migrations needed
- No changes to the mobile app required
- No changes to other backend files required
- Simply restart the Flask server after applying the fix
