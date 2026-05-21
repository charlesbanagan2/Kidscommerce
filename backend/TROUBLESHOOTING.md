# Troubleshooting: "No products available at the moment"

## Issue Summary
Your Flask app connects to Supabase successfully, but the homepage shows no products.

## Root Causes (in order of likelihood)

### 1. **Empty Product Table** (Most Likely)
The `product` table exists but has no approved/active products.

**Check:**
```bash
python check_products.py
```

**Fix:**
```bash
python seed_products.py
```

---

### 2. **Row-Level Security (RLS) Blocking Access**
Supabase RLS policies may be blocking SELECT queries from your direct PostgreSQL connection.

**Check RLS Status:**
```sql
-- In Supabase SQL Editor
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies 
WHERE tablename = 'product';
```

**Fix Option A - Disable RLS (Development Only):**
```sql
-- In Supabase SQL Editor
ALTER TABLE product DISABLE ROW LEVEL SECURITY;
```

**Fix Option B - Add Bypass Policy:**
```sql
-- In Supabase SQL Editor
CREATE POLICY "Allow all access for service role"
ON product
FOR ALL
TO authenticated, anon
USING (true)
WITH CHECK (true);
```

**Fix Option C - Use Service Role Key:**
Make sure your `.env` has:
```
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

---

### 3. **Database Connection Using Wrong Credentials**
The app might be connecting but with limited permissions.

**Check:**
1. Open Supabase Dashboard → Settings → Database
2. Verify your connection string matches `.env`
3. Make sure you're using the **Transaction Pooler** connection string
4. Ensure the password is correct (including the `@` symbol)

**Your current connection:**
```
postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce@1234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
```

---

### 4. **App Still in REST API Mode**
The code was forcing REST API mode instead of using direct PostgreSQL.

**Fixed in latest update:**
- Changed `DB_AVAILABLE = False` to `DB_AVAILABLE = True`
- Added proper connection testing
- Restart your Flask app after the fix

---

## Step-by-Step Diagnosis

### Step 1: Run Diagnostic Script
```bash
cd c:\Users\mnban\OneDrive\Desktop\kids\backend
python check_products.py
```

**Expected Output:**
```
✓ Database connection successful!
✓ 'product' table exists
   Total products: X
   Approved/Active products: Y
```

### Step 2: Check for Products
If diagnostic shows **0 approved products**:
```bash
python seed_products.py
```

### Step 3: Restart Flask App
```bash
# Stop current Flask app (Ctrl+C)
python app.py
```

### Step 4: Test Homepage
Visit: `http://localhost:5000/`

---

## Quick Fixes

### Fix 1: Seed Sample Products
```bash
python seed_products.py
```

### Fix 2: Approve Existing Products (if any)
```sql
-- In Supabase SQL Editor
UPDATE product 
SET status = 'approved' 
WHERE status = 'pending';
```

### Fix 3: Disable RLS Temporarily
```sql
-- In Supabase SQL Editor
ALTER TABLE product DISABLE ROW LEVEL SECURITY;
ALTER TABLE category DISABLE ROW LEVEL SECURITY;
ALTER TABLE "user" DISABLE ROW LEVEL SECURITY;
```

---

## Verification Checklist

- [ ] Database connection successful (`check_products.py` passes)
- [ ] Product table exists and has data
- [ ] At least one product has status 'approved' or 'active'
- [ ] RLS policies allow SELECT queries (or RLS is disabled)
- [ ] Flask app restarted after configuration changes
- [ ] Homepage loads without errors
- [ ] Products display on homepage

---

## Still Not Working?

### Check Flask Logs
Look for these messages when starting Flask:
```
[INFO] Using Supabase database: postgresql+psycopg2://postgres...
[OK] Direct PostgreSQL connection successful
```

### Check Browser Console
1. Open homepage
2. Press F12 → Console tab
3. Look for JavaScript errors

### Manual Database Query
```sql
-- In Supabase SQL Editor
SELECT id, name, status, stock 
FROM product 
WHERE status IN ('approved', 'active')
LIMIT 10;
```

If this returns products but homepage doesn't show them, the issue is in the Flask app logic.

---

## Contact Points

If none of the above works, provide:
1. Output of `python check_products.py`
2. Flask startup logs
3. Browser console errors
4. Result of manual SQL query above
