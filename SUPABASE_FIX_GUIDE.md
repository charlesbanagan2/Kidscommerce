# Supabase Connection Recovery Guide

## Quick Fix Steps

Follow these steps in order to restore your database connection.

### Step 1: Verify Your Credentials Are Valid

```powershell
cd c:\Users\mnban\OneDrive\Desktop\kids
python validate_supabase_credentials.py
```

This will check if all required credentials are in your `.env` file.

**If you see errors:** Your `.env` is missing credentials. Go to Step 2.

**If you see only warnings:** Your config looks OK. Go to Step 3.

---

### Step 2: Get Fresh Credentials from Supabase

1. **Visit Supabase Console:**
   - Go to https://supabase.com
   - Log in with your account

2. **Select Your Project:**
   - Look for the project: `qkdacoawexaxejljfihh`
   - Click on it

3. **Check Project Status:**
   - Does your project still exist?
   - Is it showing as "Active" (not paused/deleted)?
   
   **If deleted/paused:** You'll need to create a new one (see Step 4)

4. **Get Connection Details:**
   - Go to **Settings** → **Database**
   - Look for the **Connection Info** section
   - You should see:
     - Host: `db.qkdacoawexaxejljfihh.supabase.co`
     - Port: `6543`
     - Database: `postgres`
     - User: `postgres`
     - Password: (your database password)

5. **Get API Keys:**
   - Go to **Settings** → **API**
   - Copy:
     - `Project URL` (this is SUPABASE_URL)
     - `anon public` key (this is SUPABASE_KEY)
     - `service_role` key (this is SUPABASE_SERVICE_KEY)

---

### Step 3: Update Your `.env` File

Open `backend/.env` and update these values:

```env
SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co
SUPABASE_KEY=YOUR_ANON_PUBLIC_KEY_HERE
SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_DB_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=YOUR_PASSWORD_HERE
SUPABASE_DB_NAME=postgres
SUPABASE_DB_HOST=db.qkdacoawexaxejljfihh.supabase.co
SUPABASE_DB_PORT=6543
```

**Important:** Replace `YOUR_PASSWORD_HERE` with your actual database password from Supabase!

---

### Step 4: Test the Connection

```powershell
python fix_supabase.py
```

This will:
- ✓ Check DNS resolution
- ✓ Test TCP connection to port 6543
- ✓ Try to connect with SQLAlchemy
- ✓ Verify your database is working

**Expected output:**
```
[STEP 1] Network Connectivity Check
  1.2 Testing DNS Resolution...
    ✓ db.qkdacoawexaxejljfihh.supabase.co resolves to 1.2.3.4

[STEP 3] Test Database Credentials
  3.2 Testing SQLAlchemy Connection...
    ✓ SQLAlchemy connection: SUCCESSFUL!
```

---

### Step 5: Start Your Flask App

Once the connection test passes:

```powershell
cd backend
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
[OK] Email Verification API initialized
```

---

## If You Still Get Errors

### Error: "DNS cannot resolve host"

**Cause:** Your computer cannot reach Supabase servers

**Solutions:**
1. Check your internet connection:
   ```powershell
   ping google.com
   ```

2. Flush DNS cache:
   ```powershell
   ipconfig /flushdns
   ```

3. Change your DNS server to Google DNS:
   - Windows Settings → Network & Internet → WiFi/Ethernet (your connection)
   - Properties → Edit DNS settings
   - Set to: `8.8.8.8`

4. Check Supabase status:
   - Visit https://status.supabase.com
   - Look for incidents in your region

---

### Error: "Connection timeout" or "Cannot connect to port 6543"

**Cause:** Supabase server is down or unreachable

**Solutions:**
1. Check if Supabase is down:
   - Visit https://status.supabase.com
   - Look for any ongoing incidents

2. Try using a different network:
   - Try mobile hotspot
   - Try a different WiFi network

3. Check your firewall:
   - Supabase uses port 6543
   - Your firewall may be blocking it
   - Try temporarily disabling firewall

4. If still failing, create a new Supabase project (see below)

---

### Error: "Invalid password" or "Authentication failed"

**Cause:** Your database password is incorrect

**Solutions:**
1. Get correct password from Supabase:
   - Go to https://supabase.com → Your Project
   - Settings → Database
   - Copy the exact password

2. Make sure password is URL-encoded in `.env`:
   - If password is: `Kidscommerce@1234`
   - In URL it should be: `Kidscommerce%401234` (@ becomes %40)

3. Example correct URL:
   ```
   postgresql+psycopg2://postgres:Kidscommerce%401234@db.qkdacoawexaxejljfihh.supabase.co:6543/postgres
   ```

---

## Create a New Supabase Project (If Yours Is Deleted)

If your project doesn't exist anymore:

1. **Go to Supabase:**
   - Visit https://supabase.com
   - Click "New Project"

2. **Create Project:**
   - Project name: `kids-commerce` (or anything)
   - Database password: `Kidscommerce@1234` (use your original password)
   - Region: (choose closest to you)
   - Click "Create new project"

3. **Wait for initialization:**
   - This takes 5-10 minutes
   - You'll see a progress bar

4. **Get Connection Details:**
   - Once done, go to Settings → Database
   - Copy all connection details
   - Update your `backend/.env` file

5. **Important:** You'll need to recreate your database schema
   - This means re-running any SQL migrations
   - Ask if you need help with this

---

## Quick Summary

| Step | Command | What It Does |
|------|---------|-------------|
| 1 | `python validate_supabase_credentials.py` | Check if .env has all required values |
| 2 | Visit https://supabase.com | Get your connection details |
| 3 | Update `backend/.env` | Put your credentials in the file |
| 4 | `python fix_supabase.py` | Test if connection works |
| 5 | `python app.py` | Start your Flask app |

---

## Still Need Help?

If after trying all of this you still get errors:

1. Check Supabase status: https://status.supabase.com
2. Try the SQLite fallback (see bottom of this file)
3. Contact Supabase support: https://supabase.com/docs/support

---

## Temporary Fallback: Use SQLite

If Supabase is completely unavailable, you can use SQLite for development:

```powershell
python switch_to_sqlite.py
```

This will:
- Create a local SQLite database
- Update your `.env` to use it
- Let your app work without Supabase

**Note:** SQLite is for development only. Switch back to Supabase before deploying to production.

---

**Good luck! Let me know if you need help with any of these steps.** 🚀
