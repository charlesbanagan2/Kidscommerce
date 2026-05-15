# QUICK FIX: Cart Sequence Error

## Problem
You're getting this error when clicking "Buy Now":
```
duplicate key value violates unique constraint "cart_pkey"
DETAIL: Key (id)=(1) already exists.
```

## Solution
Run this SQL in your Supabase SQL Editor:

```sql
-- Fix the cart table sequence
SELECT setval('cart_id_seq', COALESCE((SELECT MAX(id) FROM cart), 0) + 1, false);
```

## Steps:
1. Go to your Supabase Dashboard
2. Click on "SQL Editor" in the left sidebar
3. Paste the SQL command above
4. Click "Run" or press Ctrl+Enter
5. Try "Buy Now" again - it should work!

## What This Does:
- Finds the highest ID currently in the cart table
- Resets the auto-increment sequence to start from the next available number
- Prevents duplicate ID conflicts

## Alternative: Clear Cart Table (if above doesn't work)
If you want to start fresh:

```sql
-- Delete all cart items and reset sequence
TRUNCATE cart RESTART IDENTITY CASCADE;
```

⚠️ WARNING: This will delete ALL cart items for ALL users!

## After Fix:
- "Buy Now" should work normally
- "Add to Cart" should work normally
- No more duplicate key errors
