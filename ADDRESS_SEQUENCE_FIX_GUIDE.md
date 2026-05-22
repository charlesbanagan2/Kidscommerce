# 🔧 Fix Address Sequence Error

## Problem
```
duplicate key value violates unique constraint "address_pkey"
Key (id)=(5) already exists
```

This happens when the database sequence (auto-increment counter) gets out of sync with the actual data.

## Quick Fix - Choose One Method

### Method 1: Run Python Script (Easiest)

```bash
cd c:\Users\mnban\OneDrive\Desktop\kids\backend
python fix_address_sequence.py
```

This will automatically fix the sequence.

### Method 2: Run SQL in Supabase Dashboard (Recommended)

1. Go to [Supabase SQL Editor](https://app.supabase.com/project/qkdacoawexaxejljfihh/sql)

2. Copy and paste this SQL:

```sql
-- Fix address sequence
SELECT setval('address_id_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);

-- Verify the fix
SELECT 
    'address' as table_name,
    (SELECT MAX(id) FROM address) as max_id,
    currval('address_id_seq') as sequence_value;
```

3. Click **Run**

4. Check the result - `sequence_value` should be greater than `max_id`

### Method 3: Fix All Sequences at Once

If you're getting similar errors on other tables, run this in Supabase SQL Editor:

```sql
-- Fix all sequences
SELECT setval('address_id_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);
SELECT setval('user_id_seq', (SELECT COALESCE(MAX(id), 1) FROM "user"), true);
SELECT setval('product_id_seq', (SELECT COALESCE(MAX(id), 1) FROM product), true);
SELECT setval('order_id_seq', (SELECT COALESCE(MAX(id), 1) FROM "order"), true);
SELECT setval('cart_id_seq', (SELECT COALESCE(MAX(id), 1) FROM cart), true);
```

## Why This Happens

The sequence gets out of sync when:
1. Data is imported with specific IDs
2. Manual INSERT statements with explicit IDs
3. Database restore from backup
4. Testing with hardcoded IDs

## Test the Fix

After running the fix, try registering again:

1. Go to: http://172.20.10.12:5000/register-buyer
2. Fill in the registration form
3. Enter your address details
4. Submit

It should work now! ✅

## Verify the Fix

Run this SQL to check if the sequence is fixed:

```sql
SELECT 
    (SELECT MAX(id) FROM address) as max_id_in_table,
    currval('address_id_seq') as current_sequence,
    nextval('address_id_seq') as next_id_will_be;
```

Expected result:
- `next_id_will_be` should be greater than `max_id_in_table`

## Prevent This in the Future

When inserting test data, don't specify IDs:

❌ **Bad:**
```sql
INSERT INTO address (id, user_id, label, ...) VALUES (5, 70, 'Home', ...);
```

✅ **Good:**
```sql
INSERT INTO address (user_id, label, ...) VALUES (70, 'Home', ...);
-- Let the database auto-generate the ID
```

## Quick Commands

### Check current sequence status:
```sql
SELECT currval('address_id_seq');
```

### Check max ID in table:
```sql
SELECT MAX(id) FROM address;
```

### Reset sequence manually:
```sql
-- Replace 100 with a number higher than your max ID
SELECT setval('address_id_seq', 100, false);
```

## Troubleshooting

### Error: "sequence does not exist"
The sequence might have a different name. Try:
```sql
-- Find the sequence name
SELECT pg_get_serial_sequence('address', 'id');

-- Use the result in setval
SELECT setval('your_sequence_name_here', (SELECT MAX(id) FROM address), true);
```

### Error: "permission denied"
You need to use the service key. Make sure you're logged into Supabase dashboard.

### Still getting the error after fix
1. Restart your backend server
2. Clear your browser cache
3. Try registering with a different email

---

## Summary

**Fastest Fix:**
1. Go to Supabase SQL Editor
2. Run: `SELECT setval('address_id_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);`
3. Try registering again

**Status:** ✅ Ready to fix!

---

**Supabase SQL Editor:** https://app.supabase.com/project/qkdacoawexaxejljfihh/sql
