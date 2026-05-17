# 🔧 Fix Database Connection Error

## Problem
Your Flask app cannot connect to Supabase because the hostname `db.qkdacoawexaxejljfihh.supabase.co` cannot be resolved. This usually means:

✅ **One of these is true:**
1. ❌ The Supabase project was deleted or is inactive
2. ❌ Your credentials in `.env` are outdated
3. ❌ Your Supabase project is in a different region

---

## ✅ Solution 1: Update Your Supabase Credentials (Recommended if you have an active project)

### Steps:
1. **Go to Supabase Dashboard**
   - Visit https://app.supabase.com
   - Log in to your account
   - Select your project

2. **Get New Connection String**
   - Click "Settings" → "Database" 
   - Scroll to "Connection string"
   - Copy the PostgreSQL connection string

3. **Update .env file**
   - Open `backend/.env`
   - Find `SUPABASE_DB_URL` 
   - Replace it with your new connection string
   - Example: `postgresql+psycopg2://postgres:PASSWORD@new-host.supabase.co:6543/postgres`

4. **Update individual credentials**
   ```
   SUPABASE_DB_HOST=your-new-host.supabase.co
   SUPABASE_DB_PORT=6543
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your_password
   SUPABASE_DB_NAME=postgres
   ```

5. **Test Connection**
   ```bash
   python diagnose_supabase.py
   ```

---

## ✅ Solution 2: Use Local PostgreSQL (Best for Development)

This is the **easiest and fastest** option for local development.

### Steps:

**On Windows:**

1. **Install PostgreSQL**
   - Download from: https://www.postgresql.org/download/windows/
   - Run installer and remember your password
   - Default port is 5432

2. **Create a local database**
   ```powershell
   # Open PowerShell as Administrator
   psql -U postgres
   ```
   Then run in psql:
   ```sql
   CREATE DATABASE kids_commerce_dev;
   \q
   ```

3. **Update .env**
   ```
   SUPABASE_DB_HOST=localhost
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your_postgres_password
   SUPABASE_DB_NAME=kids_commerce_dev
   SUPABASE_DB_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/kids_commerce_dev
   ```

4. **Run migrations (if you have them)**
   ```bash
   cd backend
   python -m flask db upgrade
   ```

5. **Test**
   ```bash
   python diagnose_supabase.py
   ```

---

## ✅ Solution 3: Use Docker PostgreSQL (No Installation Needed)

If you don't want to install PostgreSQL, use Docker:

```bash
# Start PostgreSQL in Docker
docker run --name kids_db -e POSTGRES_PASSWORD=testpass -p 5432:5432 -d postgres:15

# Then use in .env:
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=testpass
SUPABASE_DB_NAME=postgres
```

---

## ✅ What I've Done to Fix the Error

I've updated your Flask app to **handle database connection errors gracefully**:

### Changes Made:
1. ✅ Added error handler for database connection failures
2. ✅ Wrapped the `index()` route with try-catch
3. ✅ App won't crash when database is unavailable
4. ✅ Shows a helpful maintenance page instead of a traceback

### What happens now:
- If database can't connect → Shows "Service Under Maintenance" page (HTTP 503)
- User can still see the page without database temporarily
- Error message explains what's wrong

---

## 🧪 Quick Test After Fixing Database

Once you fix your database connection:

```bash
cd backend
python diagnose_supabase.py  # Should show ✅ all green

# Then try running Flask
python app.py
# Visit http://localhost:5000/
```

---

## 📞 Need Help?

**Check the diagnostic output:**
```bash
python diagnose_supabase.py
```

This will tell you:
- ✅ DNS Resolution: Is the hostname correct?
- ✅ Port Connectivity: Can you reach the database?
- 💡 Recommendations: What to do next

---

**The error handling is in place. Now just fix your database configuration! 🚀**
