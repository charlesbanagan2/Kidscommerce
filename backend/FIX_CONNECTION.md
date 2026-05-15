# Fix Supabase Connection - Reduce 968ms Latency

## Problem
Your simple `SELECT 1` query takes **968ms** - this is EXTREMELY slow!
Normal should be 10-50ms.

## Solution: Use the Correct Connection String

### Step 1: Get Your Connection Strings from Supabase

1. Go to: https://app.supabase.com/project/_/settings/database
2. Scroll to "Connection string" section
3. You'll see THREE options:
   - **URI** (Direct connection - port 5432)
   - **Session mode** (port 6543) 
   - **Transaction mode** (port 6543) ← **USE THIS ONE**

### Step 2: Choose Transaction Mode

**Transaction mode** is fastest for web applications like yours.

Example format:
```
postgresql://postgres.qkdacoawexaxejljfihh:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

Key differences:
- ✅ Has `.pooler.` in the hostname
- ✅ Uses port `6543`
- ✅ Says "Transaction" mode in Supabase dashboard

### Step 3: Update Your .env File

Find your `.env` or `supabase.env` file and update:

```env
SUPABASE_DB_URL=postgresql://postgres.qkdacoawexaxejljfihh:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**Important:** 
- Replace `[YOUR-PASSWORD]` with your actual database password
- Make sure it has `.pooler.` in the hostname
- Port must be `6543`

### Step 4: Check Your Region

Your Supabase project region matters! Check:
1. Go to: https://app.supabase.com/project/_/settings/general
2. Look at "Region"
3. If it's far from you (e.g., you're in Asia but region is US), that's why it's slow

**Your current connection shows:** `aws-0-ap-southeast-1`
- This is **Singapore region** (Southeast Asia)
- If you're in Philippines/Asia, this is GOOD
- If you're in US/Europe, this is BAD (high latency)

### Step 5: Restart Server

```bash
# Stop server (Ctrl+C)
python app.py
```

### Step 6: Test Again

```bash
python diagnose_advanced.py
```

**Expected result:** Simple SELECT 1 should be **10-50ms** (not 968ms!)

---

## Still Slow After Fixing?

### Option A: Your Internet Connection
- Test your internet speed: https://fast.com
- If < 10 Mbps, that could be the issue
- Try from a different network

### Option B: Supabase Free Tier Limits
- Free tier has performance limits
- Consider upgrading to Pro: https://supabase.com/pricing
- Pro tier is much faster

### Option C: Use Direct Connection (Temporary Test)

Try the **direct connection** (port 5432) to see if pooler is the issue:

```env
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.qkdacoawexaxejljfihh.supabase.co:5432/postgres
```

If this is faster, use it. But pooler is usually better for production.

---

## Summary

1. ✅ Get Transaction mode connection string from Supabase
2. ✅ Update SUPABASE_DB_URL in .env
3. ✅ Verify region is close to you
4. ✅ Restart server
5. ✅ Test - should be 10-50ms (not 968ms!)
