# FIX: Orders Not Showing in My Orders Tab & Rider Dashboard

## 🔴 PROBLEM
- **Buyer**: "My Orders" tab shows no orders even after refresh and waiting
- **Rider**: Order #49 not showing in rider dashboard orders tab
- **Root Cause**: Supabase RLS (Row Level Security) policies are blocking order queries

## 🔍 WHY THIS HAPPENS

Your backend uses **service_role key** which bypasses RLS, so orders are created successfully in the database. However, when the mobile app queries orders, it uses the **anon key** which is subject to RLS policies.

The current RLS policies have issues:
1. **Type mismatch**: `current_setting('app.user_id')` returns a string, but comparing with bigint columns
2. **Missing OR conditions**: Riders need to see orders where `rider_id IS NULL` AND `status = 'ready_for_pickup'`
3. **Incomplete policies**: Not all access patterns are covered

## ✅ SOLUTION

### Step 1: Run the SQL Fix Script

1. **Open Supabase Dashboard**
   - Go to https://supabase.com
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Paste the SQL Script**
   - Open the file: `backend/fix_order_rls_policies.sql`
   - Copy ALL the content
   - Paste into Supabase SQL Editor

4. **Execute the Script**
   - Click "Run" button
   - Wait for completion message: ✅ ORDER RLS POLICIES FIXED!

### Step 2: Verify the Fix

Run this verification query in Supabase SQL Editor:

```sql
-- Check if policies are created
SELECT 
    tablename,
    COUNT(*) as policy_count
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item')
GROUP BY tablename;
```

**Expected Result:**
- `order`: 7 policies
- `order_item`: 4 policies

### Step 3: Test in Mobile App

1. **For Buyers:**
   - Open mobile app
   - Login as buyer
   - Go to "My Orders" tab
   - Pull to refresh
   - Orders should now appear

2. **For Riders:**
   - Open mobile app
   - Login as rider
   - Go to "Orders" tab
   - Should see:
     - Assigned orders (where rider_id = your ID)
     - Available orders (status = 'ready_for_pickup' AND rider_id IS NULL)

## 🔧 WHAT THE FIX DOES

### Order Table Policies (7 policies)

1. **Buyers can view own orders**
   - Allows buyers to see orders where `buyer_id` matches their user ID
   - Handles both string and bigint type comparisons

2. **Sellers can view orders with their products**
   - Allows sellers to see orders containing their products
   - Uses JOIN with `order_item` and `product` tables

3. **Riders can view assigned orders**
   - Allows riders to see orders where:
     - `rider_id` = their ID (assigned orders)
     - `picked_up_by` = their ID (picked up orders)
     - `delivered_by` = their ID (delivered orders)
     - `status = 'ready_for_pickup' AND rider_id IS NULL` (available orders)

4. **Buyers can create orders**
   - Allows buyers to insert new orders

5. **Buyers can update own orders**
   - Allows buyers to update their orders (cancel, confirm delivery)

6. **Sellers can update orders with their products**
   - Allows sellers to update order status (process, ship)

7. **Riders can update assigned orders**
   - Allows riders to update orders they're assigned to

### Order Item Table Policies (4 policies)

1. **Buyers can view own order items**
   - Allows buyers to see items in their orders

2. **Sellers can view order items for their products**
   - Allows sellers to see order items for their products

3. **Riders can view items in assigned orders**
   - Allows riders to see items in orders they're assigned to
   - Also allows viewing items in available orders

4. **Allow order item creation**
   - Allows creating order items during checkout

## 🎯 KEY IMPROVEMENTS

### 1. Type Safety
```sql
-- OLD (fails):
buyer_id = current_setting('app.user_id', true)::bigint

-- NEW (works):
buyer_id::text = current_setting('app.user_id', true)
OR buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
```

### 2. Rider Available Orders
```sql
-- NEW: Riders can see unassigned orders ready for pickup
OR (status = 'ready_for_pickup' AND rider_id IS NULL)
```

### 3. Multiple Rider Fields
```sql
-- Handles all rider assignment scenarios
rider_id = user_id
OR picked_up_by = user_id
OR delivered_by = user_id
```

## 🧪 TESTING CHECKLIST

### Buyer Testing
- [ ] Login as buyer
- [ ] Navigate to "My Orders" tab
- [ ] Verify orders appear
- [ ] Check order details load correctly
- [ ] Test pull-to-refresh
- [ ] Verify order status updates

### Rider Testing
- [ ] Login as rider
- [ ] Navigate to "Orders" tab
- [ ] Verify assigned orders appear
- [ ] Verify available orders appear (ready_for_pickup)
- [ ] Test accepting an order
- [ ] Verify order moves to "My Orders"
- [ ] Test order status updates (pickup, deliver)

### Seller Testing
- [ ] Login as seller
- [ ] Navigate to "Orders" tab
- [ ] Verify orders with seller's products appear
- [ ] Test order status updates

## 🚨 TROUBLESHOOTING

### Issue: Orders still not showing

**Check 1: Verify RLS is enabled**
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item');
```
Both should show `rowsecurity = true`

**Check 2: Verify policies exist**
```sql
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item')
ORDER BY tablename, policyname;
```
Should show 7 policies for `order` and 4 for `order_item`

**Check 3: Check backend is setting user_id**
Look for this in your backend code:
```python
# Should be setting app.user_id in Supabase client
supabase.postgrest.auth(token)
supabase.rpc('set_config', {
    'setting': 'app.user_id',
    'value': str(user_id)
})
```

**Check 4: Verify orders exist in database**
```sql
SELECT id, buyer_id, rider_id, status, created_at
FROM "order"
ORDER BY created_at DESC
LIMIT 10;
```

### Issue: Specific order not showing (e.g., Order #49)

**Check order details:**
```sql
SELECT 
    id,
    buyer_id,
    rider_id,
    picked_up_by,
    delivered_by,
    status,
    created_at
FROM "order"
WHERE id = 49;
```

**Check if rider should see it:**
- If `rider_id` matches rider's user ID → Should see it
- If `status = 'ready_for_pickup'` AND `rider_id IS NULL` → Should see it
- Otherwise → Won't see it (correct behavior)

### Issue: Backend errors

**Check backend logs:**
```bash
# Look for RLS-related errors
tail -f backend/server.log | grep -i "rls\|policy\|permission"
```

**Common errors:**
- "new row violates row-level security policy" → Policy too restrictive
- "permission denied for table" → Missing GRANT statement
- "relation does not exist" → Table name typo

## 📝 ADDITIONAL NOTES

### Backend Service Role Key
Your Flask backend uses the **service_role key** which bypasses RLS. This is correct and should not be changed. The service role key allows the backend to:
- Create orders on behalf of users
- Update order status
- Query all orders for admin purposes

### Mobile App Anon Key
Your mobile app uses the **anon key** which is subject to RLS. This is also correct. The RLS policies ensure users can only see their own data.

### Setting User Context
Make sure your backend sets the user context when making queries on behalf of users:

```python
# In your token_required decorator or similar
def set_user_context(user_id):
    supabase.rpc('set_config', {
        'setting': 'app.user_id',
        'value': str(user_id),
        'is_local': True
    })
```

## 🎉 EXPECTED OUTCOME

After applying this fix:

1. **Buyers** will see all their orders in "My Orders" tab
2. **Riders** will see:
   - Orders assigned to them
   - Available orders ready for pickup
3. **Sellers** will see orders containing their products
4. **Order #49** will appear in the correct rider's dashboard
5. **Real-time updates** will work correctly
6. **Pull-to-refresh** will fetch latest orders

## 📞 SUPPORT

If issues persist after applying this fix:

1. Check Supabase logs (Dashboard → Logs → Postgres Logs)
2. Check backend logs (`backend/server.log`)
3. Check mobile app console logs
4. Verify the SQL script ran successfully (no errors)
5. Verify policies were created (run verification queries)

---

**Last Updated**: 2025-01-05
**Status**: Ready to deploy
**Priority**: CRITICAL - Affects core functionality
