# STORE LOGO FIX - Mobile App

## PROBLEMA
Nawala ang mga store logos sa mobile app kahit naka-live na ang server.

## ROOT CAUSE
Ang `_safe_upload_url()` function at ilang API endpoints ay hindi properly handling ang store logo URLs na naka-save sa database as `/static/uploads/documents/xxx.png`.

Ang code ay nag-aassume na ang store_logo ay plain filename lang (e.g., `logo.png`) at dinagdagan pa ng `/static/uploads/` prefix, resulting in wrong URLs like:
- `/static/uploads//static/uploads/documents/logo.png` ❌

## SOLUSYON

### 1. Fixed `_safe_upload_url()` function (line 15258)
**BEFORE:**
```python
def _safe_upload_url(filename):
    if not filename:
        return None
    # If already a full URL or starts with /static/, return as-is
    if filename.startswith('http') or filename.startswith('/static/'):
        return filename
    try:
        return url_for('static', filename=f'uploads/{filename}')
    except Exception:
        return f'/static/uploads/{filename}'
```

**AFTER:**
```python
def _safe_upload_url(filename):
    if not filename:
        return None
    # If already a full URL, return as-is
    if filename.startswith('http'):
        return filename
    # If starts with /static/, return as-is (already a valid path)
    if filename.startswith('/static/'):
        return filename
    # If starts with just /, assume it's a valid path from root
    if filename.startswith('/'):
        return filename
    # Otherwise, assume it's just a filename in uploads folder
    try:
        return url_for('static', filename=f'uploads/{filename}')
    except Exception:
        return f'/static/uploads/{filename}'
```

### 2. Fixed Mobile API Endpoints (lines 18171, 18257)
Pinalitan ang:
```python
'store_logo': url_for('static', filename=f'uploads/{seller_app.get("store_logo")}')
```

Naging:
```python
'store_logo': _safe_upload_url(seller_app.get('store_logo'))
```

## FILES CHANGED
- `backend/app.py` - Fixed `_safe_upload_url()` and 2 API endpoints

## GIT COMMIT
- Commit: `ecfba97` - "fix: properly handle store_logo URLs in mobile API"
- Branch: `main`
- Status: ✅ Pushed to GitHub

## TESTING
1. **Redeploy ang Render service** para ma-apply ang fix
2. **Restart ang mobile app** para ma-refresh ang data
3. **Check kung lumalabas na ang store logos** sa:
   - Product detail screen
   - Store detail screen
   - Product listings

## EXPECTED RESULT
Ang store logos ay dapat lumabas na sa mobile app with correct URLs:
- `https://kidscommerce-backend.onrender.com/static/uploads/documents/xxx.png` ✅

## NOTES
- Ang fix ay backward compatible - gumagana pa rin for plain filenames
- Walang kailangang database changes
- Automatic na ang fix pagkatapos ng Render redeploy
