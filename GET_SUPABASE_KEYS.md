# 🔑 HOW TO GET YOUR SUPABASE API KEYS

## Step-by-Step Instructions

### 1. Go to Supabase Dashboard
Open this link in your browser:
```
https://supabase.com/dashboard/project/qkdacoawexaxejljfihh/settings/api
```

### 2. Find the API Keys Section
You'll see a page titled **"API Settings"** with two important keys:

#### A. Project API keys
- **anon public** - This is your public key (safe to use in client-side code)
- **service_role** - This is your secret key (only use server-side, bypasses RLS)

### 3. Copy the Keys
Both keys are **JWT tokens** that look like this:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrZGFjb2F3ZXhheGVqbGpmaWhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ1OTI4MDAsImV4cCI6MjA1MDE2ODgwMH0.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Click the "Copy" button** next to each key.

### 4. Update Your .env File

Open `backend/.env` and replace these lines:

**Current (WRONG)**:
```env
SUPABASE_KEY="sb_publishable_PcSjw7T6f7D4tj3s8SxZKg_IqTuUhWM"
SUPABASE_SERVICE_KEY="sb_secret_Kxo54KzgPd8haK3Za_-VkQ_AoTWJUhX"
```

**Replace with (CORRECT)**:
```env
SUPABASE_KEY="eyJhbGci...PASTE_YOUR_ANON_PUBLIC_KEY_HERE"
SUPABASE_SERVICE_KEY="eyJhbGci...PASTE_YOUR_SERVICE_ROLE_KEY_HERE"
```

### 5. Save and Restart Server

After updating the keys:
```bash
cd backend
python app.py
```

---

## 🎯 What Each Key Does

### SUPABASE_KEY (anon public)
- Used for **client-side** operations (mobile app, web frontend)
- Respects Row Level Security (RLS) policies
- Safe to expose in mobile apps
- Used for: User authentication, reading public data

### SUPABASE_SERVICE_KEY (service_role)
- Used for **server-side** operations (backend API)
- **Bypasses** Row Level Security (RLS)
- **NEVER expose** in client-side code
- Used for: Admin operations, bulk updates, migrations

---

## ✅ How to Verify Keys Are Working

After updating and restarting server, check the logs:

**Good** ✅:
```
[OK] Direct PostgreSQL connection successful
[OK] Product chat API registered
[OK] Notification API registered
```

**Bad** ❌:
```
[ERROR] Invalid Supabase credentials
[ERROR] Authentication failed
```

---

## 🔐 Security Reminders

- ✅ Keep `SUPABASE_SERVICE_KEY` secret
- ✅ Never commit `.env` to git (already in `.gitignore`)
- ✅ Use `SUPABASE_KEY` (anon) in mobile app
- ✅ Use `SUPABASE_SERVICE_KEY` (service_role) in backend only
- ❌ Never expose service_role key in mobile app or frontend

---

## 📸 Visual Guide

When you open the API settings page, you'll see:

```
┌─────────────────────────────────────────────────────┐
│ API Settings                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Project URL                                         │
│ https://qkdacoawexaxejljfihh.supabase.co          │
│                                                     │
│ Project API keys                                    │
│                                                     │
│ anon public                                         │
│ eyJhbGci... [Copy button]                          │
│                                                     │
│ service_role                                        │
│ eyJhbGci... [Copy button] ⚠️ Secret                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

Click the **[Copy]** button next to each key!

---

## 🆘 Troubleshooting

**Q: I don't see the API keys page**
- Make sure you're logged in to Supabase
- Make sure you have access to project `qkdacoawexaxejljfihh`

**Q: The keys are too long**
- That's normal! JWT tokens are very long (200+ characters)
- Copy the entire key including all dots (.)

**Q: Server still shows errors after updating**
- Make sure you saved the `.env` file
- Make sure you restarted the server (Ctrl+C then `python app.py`)
- Check for typos in the keys

---

**Next Step**: After getting the keys, restart your server and test!
