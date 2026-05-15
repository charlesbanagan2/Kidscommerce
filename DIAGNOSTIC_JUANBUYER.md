# 🔍 DIAGNOSTIC: juanbuyer@gmail.com Orders Not Showing

## 🎯 PROBLEM

- User: juanbuyer@gmail.com
- Issue: "My Orders" tab shows no orders
- Order #49 not appearing
- Even after refresh and waiting

## 📋 DIAGNOSTIC STEPS

### Step 1: Check Database Directly

Run this in **Supabase SQL Editor**:

```sql
-- Find the user
SELECT id, email, role, status 
FROM "user" 
WHERE email = 'juanbuyer@gmail.com';

-- Check orders for this user (replace 25 with actual user id)
SELECT 
    o.id,
    o.buyer_id,
    o.status,
    o.total_amount,
    o.created_at
FROM "order" o
WHERE o.buyer_id = (SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com')
ORDER BY o.created_at DESC;

-- Check Order #49 specifically
SELECT 
    o.id,
    o.buyer_id,
    o.status,
    u.email as buyer_email
FROM "order" o
LEFT JOIN "user" u ON o.buyer_id = u.id
WHERE o.id = 49;
```

**Expected Results:**

**Scenario A: No orders found**
```
Result: 0 rows
Problem: User has no orders in database
Solution: Create a test order
```

**Scenario B: Orders found**
```
Result: Shows orders with IDs
Problem: Orders exist but not showing in app
Solution: RLS policies or API issue
```

**Scenario C: Order #49 belongs to different user**
```
Result: Order #49 buyer_email is NOT juanbuyer@gmail.com
Problem: Order #49 belongs to someone else
Solution: Check correct user
```

### Step 2: Check RLS Policies

Run this in **Supabase SQL Editor**:

```sql
-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'order' 
AND schemaname = 'public';

-- Check policies
SELECT policyname, roles, cmd
FROM pg_policies 
WHERE tablename = 'order';
```

**Expected Results:**

```
rowsecurity: true (RLS enabled)
policies: Should show 2 policies:
  - service_role_full_access
  - authenticated_can_access
```

**If different:**
- Run the CORRECT_ORDER_FIX.sql again

### Step 3: Test Backend API

Run this in **Command Prompt**:

```bash
cd backend
python test_juanbuyer_orders.py
```

**Expected Output:**

```
✅ Login successful!
✅ Got X orders
✅ Order #49 IS in the response!
```

**If shows 0 orders:**
- Backend or RLS is blocking

### Step 4: Check Backend Logs

```bash
cd backend
tail -f server.log
```

Look for:
- SQL queries being executed
- Any errors
- Filter conditions

### Step 5: Test Direct Supabase Query

Run this in **Supabase SQL Editor**:

```sql
-- Test if service_role can see orders
SELECT COUNT(*) as total_orders FROM "order";

-- Test if specific user orders exist
SELECT COUNT(*) as user_orders 
FROM "order" 
WHERE buyer_id = (SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com');
```

## 🔧 COMMON ISSUES & SOLUTIONS

### Issue 1: User Has No Orders

**Symptom:**
```sql
SELECT COUNT(*) FROM "order" WHERE buyer_id = X;
-- Returns: 0
```

**Solution:**
Create a test order:

```sql
-- Get user ID
SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com';
-- Let's say it returns 25

-- Create test order
INSERT INTO "order" (buyer_id, status, total_amount, created_at, updated_at)
VALUES (25, 'pending', 100.00, NOW(), NOW())
RETURNING id;

-- Create order item
INSERT INTO order_item (order_id, product_id, quantity, price_at_time)
VALUES (
  (SELECT id FROM "order" WHERE buyer_id = 25 ORDER BY created_at DESC LIMIT 1),
  1,  -- product_id (use existing product)
  1,  -- quantity
  100.00  -- price
);
```

### Issue 2: Order #49 Belongs to Different User

**Symptom:**
```sql
SELECT buyer_id FROM "order" WHERE id = 49;
-- Returns: 30 (not 25)
```

**Solution:**
Order #49 belongs to a different user. Check the correct user:

```sql
SELECT u.email, o.id, o.status
FROM "order" o
JOIN "user" u ON o.buyer_id = u.id
WHERE o.id = 49;
```

### Issue 3: RLS Policies Not Applied

**Symptom:**
```sql
SELECT COUNT(*) FROM pg_policies WHERE tablename = 'order';
-- Returns: 0 or wrong policies
```

**Solution:**
Run the fix again:

```bash
# Open: backend/CORRECT_ORDER_FIX.sql
# Copy all content
# Paste in Supabase SQL Editor
# Click Run
```

### Issue 4: Backend Not Using Service Role Key

**Symptom:**
Backend logs show permission errors

**Solution:**
Check `backend/supabase.env`:

```bash
# Should have:
SUPABASE_SERVICE_KEY=eyJ...  (very long key)

# NOT:
SUPABASE_KEY=eyJ...  (anon key)
```

### Issue 5: Backend Filtering Wrong User ID

**Symptom:**
Backend queries with wrong user_id

**Solution:**
Check token_required decorator:

```python
# Should set:
request.current_user_id = payload['user_id']
```

## 🎯 QUICK DIAGNOSTIC CHECKLIST

Run these in order:

- [ ] **Check 1:** User exists in database
  ```sql
  SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com';
  ```

- [ ] **Check 2:** User has orders
  ```sql
  SELECT COUNT(*) FROM "order" WHERE buyer_id = (SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com');
  ```

- [ ] **Check 3:** Order #49 exists
  ```sql
  SELECT * FROM "order" WHERE id = 49;
  ```

- [ ] **Check 4:** Order #49 belongs to juanbuyer
  ```sql
  SELECT buyer_id FROM "order" WHERE id = 49;
  -- Should match user id from Check 1
  ```

- [ ] **Check 5:** RLS policies exist
  ```sql
  SELECT COUNT(*) FROM pg_policies WHERE tablename = 'order';
  -- Should return 2
  ```

- [ ] **Check 6:** Backend is running
  ```bash
  curl http://localhost:5000/api/v1/products
  ```

- [ ] **Check 7:** Can login
  ```bash
  python backend/test_juanbuyer_orders.py
  ```

## 📊 RESULTS INTERPRETATION

### Result A: No Orders in Database
```
Check 1: ✅ User exists (id: 25)
Check 2: ❌ 0 orders
Check 3: ❌ Order #49 doesn't exist
```

**Action:** Create test orders (see Issue 1 solution)

### Result B: Orders Exist But Not Showing
```
Check 1: ✅ User exists (id: 25)
Check 2: ✅ 3 orders found
Check 3: ✅ Order #49 exists
Check 4: ✅ Order #49 belongs to user 25
Check 5: ❌ 0 policies or wrong policies
```

**Action:** Run CORRECT_ORDER_FIX.sql

### Result C: Order #49 Belongs to Different User
```
Check 1: ✅ User exists (id: 25)
Check 2: ✅ 2 orders found (not including #49)
Check 3: ✅ Order #49 exists
Check 4: ❌ Order #49 belongs to user 30 (not 25)
```

**Action:** Order #49 is not for juanbuyer@gmail.com

### Result D: Backend Not Running
```
Check 6: ❌ Connection refused
```

**Action:** Start backend
```bash
cd backend
python app.py
```

## 🚀 MOST LIKELY SOLUTIONS

### Solution 1: Run the SQL Fix (90% of cases)

```bash
# 1. Open Supabase SQL Editor
# 2. Copy: backend/CORRECT_ORDER_FIX.sql
# 3. Paste and Run
# 4. Test mobile app
```

### Solution 2: Create Test Order (if no orders exist)

```sql
-- Get user ID
SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com';

-- Create order (replace 25 with actual user id)
INSERT INTO "order" (buyer_id, status, total_amount, created_at, updated_at)
VALUES (25, 'pending', 100.00, NOW(), NOW());
```

### Solution 3: Restart Backend

```bash
cd backend
# Stop current process (Ctrl+C)
python app.py
```

## 📞 NEXT STEPS

1. **Run diagnostic SQL** (Step 1)
2. **Check results** against scenarios above
3. **Apply appropriate solution**
4. **Test mobile app**
5. **Report results**

---

**Files to use:**
- `backend/CHECK_JUANBUYER_ORDERS.sql` - Diagnostic queries
- `backend/test_juanbuyer_orders.py` - API test script
- `backend/CORRECT_ORDER_FIX.sql` - RLS fix

**Priority:** CRITICAL
**Time:** 5-10 minutes to diagnose
