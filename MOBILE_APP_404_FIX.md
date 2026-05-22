# MOBILE APP 404 ERROR FIX

## PROBLEM
Mobile app is getting **404 Not Found** for all API endpoints:
- `/api/v1/products` - 404
- `/api/v1/wishlist` - 404
- `/api/v1/addresses` - 404
- `/api/v1/orders` - 404

## ROOT CAUSE
Possible causes:
1. **Wrong Render Start Command** - Missing `--chdir backend` or wrong working directory
2. **Old deployment** - Render deployed an old commit
3. **Flask routing issue** - API routes not registered

## SOLUTION

### STEP 1: Check Render Start Command
1. Go to: https://dashboard.render.com
2. Select service: **kids-kingdom**
3. Go to **Settings** → **Build & Deploy**
4. Check **Start Command**

**CORRECT Start Command:**
```bash
cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

OR

```bash
gunicorn --chdir backend --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

**WRONG Start Command (will cause 404):**
```bash
gunicorn app:app
```

### STEP 2: Check Build Command
**CORRECT Build Command:**
```bash
pip install -r backend/requirements.txt
```

### STEP 3: Verify Deployment
After updating the start command:
1. Click **Manual Deploy** → **Deploy latest commit**
2. Wait for deployment to complete
3. Check logs for:
   ```
   [OK] Product chat API registered
   [OK] Notification API registered
   [OK] Mobile API endpoints loaded
   ```

### STEP 4: Test API Endpoints
Test directly in browser:
```
https://kids-kingdom.onrender.com/api/v1/products?page=1&per_page=5
```

Should return JSON with products, not 404.

## ALTERNATIVE: Check Root Directory Setting

If start command is correct, check **Root Directory**:
1. Go to **Settings** → **Build & Deploy**
2. Check **Root Directory**
3. Should be: **EMPTY** or **backend**

If it's set to something else, clear it or set to `backend`.

## VERIFICATION

### Test API Endpoints
```bash
# Test products endpoint
curl https://kids-kingdom.onrender.com/api/v1/products?page=1&per_page=5

# Test health check (if exists)
curl https://kids-kingdom.onrender.com/api/health

# Test homepage (should work)
curl https://kids-kingdom.onrender.com/
```

### Expected Response
```json
{
  "products": [...],
  "total": 25,
  "page": 1,
  "per_page": 5
}
```

## CURRENT STATUS
- ✅ Website images - WORKING
- ✅ Website homepage - WORKING
- ❌ Mobile API endpoints - 404 ERROR

## NEXT STEPS
1. Check Render start command
2. Update if wrong
3. Redeploy
4. Test mobile app again
